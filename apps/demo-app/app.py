from flask import Flask, jsonify, Response
import psycopg2
import redis
import os
import time
import random

print("=" * 50)
print("🚀 STARTING APPLICATION")
print("=" * 50)

try:
    from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
    print("✓ prometheus_client imported successfully")
except ImportError as e:
    print(f"✗ ERROR importing prometheus_client: {e}")
    exit(1)

app = Flask(__name__)

REQUEST_COUNT = Counter('flask_http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('flask_http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
print("✓ Prometheus metrics created")

DB_HOST = os.getenv('DB_HOST', 'postgres')
DB_NAME = os.getenv('DB_NAME', 'appdb')
DB_USER = os.getenv('DB_USER', 'appuser')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)

def get_redis_connection():
    return redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

@app.before_request
def before_request():
    from flask import request, g
    g.start_time = time.time()

@app.after_request
def after_request(response):
    from flask import request, g
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        REQUEST_DURATION.labels(method=request.method, endpoint=request.endpoint or 'unknown').observe(duration)
        REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint or 'unknown', status=response.status_code).inc()
    return response

@app.route('/')
def home():
    return """
    <h1>🐳 Demo Monitoring App</h1>
    <p>Aplikacja z metrykami Prometheus</p>
    <ul>
        <li><a href="/health">Status aplikacji</a></li>
        <li><a href="/db-test">Test bazy danych</a></li>
        <li><a href="/cache-test">Test cache (Redis)</a></li>
        <li><a href="/metrics">📊 Metryki Prometheus</a></li>
        <li><a href="/api/slow">Wolne zapytanie (test metryk)</a></li>
        <li><a href="/api/fast">Szybkie zapytanie</a></li>
    </ul>
    <h3>Monitoring:</h3>
    <ul>
        <li><a href="http://localhost:9090" target="_blank">Prometheus UI</a></li>
    </ul>
    """

@app.route('/metrics')
def metrics():
    print("📊 /metrics endpoint called")
    try:
        output = generate_latest(REGISTRY)
        print(f"📊 Generated {len(output)} bytes of metrics")
        return Response(output, mimetype='text/plain')
    except Exception as e:
        print(f"✗ ERROR generating metrics: {e}")
        return Response(f"Error: {e}", status=500)

@app.route('/health')
def health():
    status = {'status': 'ok', 'app': 'running'}
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT version();')
        conn.close()
        status['database'] = 'connected'
    except Exception as e:
        status['database'] = f'error: {str(e)}'
    
    try:
        r = get_redis_connection()
        r.ping()
        status['redis'] = 'connected'
    except Exception as e:
        status['redis'] = f'error: {str(e)}'
    
    return jsonify(status)

@app.route('/db-test')
def db_test():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS visits (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cur.execute('INSERT INTO visits DEFAULT VALUES RETURNING id, timestamp')
        visit_id, timestamp = cur.fetchone()
        
        cur.execute('SELECT COUNT(*) FROM visits')
        total_visits = cur.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'visit_id': visit_id,
            'timestamp': str(timestamp),
            'total_visits': total_visits
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/cache-test')
def cache_test():
    try:
        r = get_redis_connection()
        counter_key = 'cache:counter'
        count = r.incr(counter_key)
        
        if count == 1:
            r.expire(counter_key, 300)
        
        return jsonify({'status': 'success', 'cache_hits': count})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/fast')
def fast_endpoint():
    return jsonify({'message': 'Fast response', 'timestamp': time.time()})

@app.route('/api/slow')
def slow_endpoint():
    delay = random.uniform(0.5, 2.0)
    time.sleep(delay)
    return jsonify({'message': 'Slow response', 'delay': f'{delay:.2f}s'})

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Flask app starting on 0.0.0.0:8000")
    print("📊 Metrics endpoint: http://localhost:8000/metrics")
    print("=" * 50)
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)
