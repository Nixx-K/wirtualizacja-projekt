from flask import Flask, jsonify
import psycopg2
import redis
import os
import time

app = Flask(__name__)

# Konfiguracja
DB_HOST = os.getenv('DB_HOST', 'postgres')
DB_NAME = os.getenv('DB_NAME', 'appdb')
DB_USER = os.getenv('DB_USER', 'appuser')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def get_redis_connection():
    return redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

@app.route('/')
def home():
    return """
    <h1>🐳 </h1>
    <p>Aplikacja działa!</p>
    <ul>
        <li><a href="/health">Sprawdź status</a></li>
        <li><a href="/db-test">Test bazy danych</a></li>
        <li><a href="/cache-test">Test cache (Redis)</a></li>
    </ul>
    """

@app.route('/health')
def health():
    status = {'status': 'ok', 'app': 'running'}
    

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT version();')
        db_version = cur.fetchone()[0]
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
    """Test Redis cache"""
    try:
        r = get_redis_connection()
        
        
        counter_key = 'cache:counter'
        
        count = r.incr(counter_key)
        
        if count == 1:
            r.expire(counter_key, 300) 
        
        #zapisywanie timestampa
        timestamp_key = f'cache:timestamp:{count}'
        r.setex(timestamp_key, 60, str(time.time()))
        
        return jsonify({
            'status': 'success',
            'cache_hits': count,
            'message': 'Wartość zapisana w cache'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
