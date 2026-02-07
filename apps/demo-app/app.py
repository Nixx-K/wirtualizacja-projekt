from flask import Flask, jsonify, Response, request, g
import psycopg2
import redis
import os
import time
import random
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY

app = Flask(__name__)

# metryki
REQUEST_COUNT = Counter('flask_http_requests_total', 'total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('flask_http_request_duration_seconds', 'request duration', ['method', 'endpoint'])

# konfiguracja z env
DB_HOST = os.getenv('DB_HOST', 'postgres')
DB_NAME = os.getenv('DB_NAME', 'bazkadanych')
DB_USER = os.getenv('DB_USER', 'userappki')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'haslotakzwanesekretne#321')
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)

def get_redis_connection():
    return redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        REQUEST_DURATION.labels(method=request.method, endpoint=request.endpoint or 'unknown').observe(duration)
        REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint or 'unknown', status=response.status_code).inc()
    return response

@app.route('/')
def home():
    return """
    <h1>demo app</h1>
    <p>aplikacja z metrykami prometheus</p>
    <ul>
        <li><a href="/health">status</a></li>
        <li><a href="/db-test">test bazy</a></li>
        <li><a href="/cache-test">test cache</a></li>
        <li><a href="/metrics">metryki</a></li>
        <li><a href="/api/slow">wolne zapytanie</a></li>
        <li><a href="/api/fast">szybkie zapytanie</a></li>
    </ul>
    """

@app.route('/metrics')
def metrics():
    return Response(generate_latest(REGISTRY), mimetype='text/plain')

@app.route('/health')
def health():
    status = {'app': 'ok'}
    try:
        conn = get_db_connection()
        conn.close()
        status['database'] = 'connected'
    except:
        status['database'] = 'error'
    try:
        r = get_redis_connection()
        r.ping()
        status['redis'] = 'connected'
    except:
        status['redis'] = 'error'
    return jsonify(status)

@app.route('/db-test')
def db_test():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS visits (id SERIAL PRIMARY KEY, ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        cur.execute('INSERT INTO visits DEFAULT VALUES RETURNING id, ts')
        visit_id, ts = cur.fetchone()
        cur.execute('SELECT COUNT(*) FROM visits')
        total = cur.fetchone()[0]
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'id': visit_id, 'total': total})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@app.route('/cache-test')
def cache_test():
    try:
        r = get_redis_connection()
        count = r.incr('hits')
        return jsonify({'status': 'success', 'hits': count})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@app.route('/api/fast')
def fast():
    return jsonify({'speed': 'fast'})

@app.route('/api/slow')
def slow():
    time.sleep(random.uniform(0.5, 2.0))
    return jsonify({'speed': 'slow'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
