from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from pathlib import Path

app = Flask(__name__, static_folder='../../website')
CORS(app)

DB_PATH = Path('/a0/usr/projects/x-manage/data/db/newsletter.db')

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('CREATE TABLE IF NOT EXISTS subscribers (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    conn.commit()
    conn.close()

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    try:
        data = request.json
        email = data.get('email')
        if not email or '@' not in email:
            return jsonify({'status': 'error', 'message': 'Invalid email'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        conn.execute('INSERT INTO subscribers (email) VALUES (?)', (email,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Subscribed!'}), 200
    except sqlite3.IntegrityError:
        return jsonify({'status': 'success', 'message': 'Already subscribed!'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8000)
