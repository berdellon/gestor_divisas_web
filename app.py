# app.py  (Flask backend + API)
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3, os
from datetime import datetime

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'data.db')

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS operaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT,
                cliente TEXT,
                importe REAL,
                usdt REAL,
                fecha TEXT,
                estado TEXT
            )
        ''')
        conn.commit()

init_db()

def row_to_dict(row):
    return {
        "id": row[0],
        "tipo": row[1],
        "cliente": row[2],
        "importe": row[3],
        "usdt": row[4],
        "fecha": row[5],
        "estado": row[6]
    }

# Páginas web
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/operaciones')
def operaciones_page():
    return render_template('operaciones.html')

# API: obtener todas las operaciones
@app.route('/api/operaciones', methods=['GET'])
def api_get_operaciones():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM operaciones ORDER BY fecha DESC")
        rows = c.fetchall()
    data = [row_to_dict(r) for r in rows]
    return jsonify(data)

# API: añadir operación
@app.route('/api/operaciones', methods=['POST'])
def api_add_operacion():
    payload = request.json or {}
    tipo = payload.get('tipo', '')
    cliente = payload.get('cliente', '')
    importe = float(payload.get('importe', 0) or 0)
    usdt = float(payload.get('usdt', 0) or 0)
    estado = payload.get('estado', 'Finalizada')
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO operaciones (tipo, cliente, importe, usdt, fecha, estado) VALUES (?, ?, ?, ?, ?, ?)",
            (tipo, cliente, importe, usdt, fecha, estado)
        )
        conn.commit()
        op_id = c.lastrowid
    return jsonify({"message": "Operación añadida", "id": op_id}), 201

# API: editar operación
@app.route('/api/operaciones/<int:op_id>', methods=['PUT'])
def api_edit_operacion(op_id):
    payload = request.json or {}
    cliente = payload.get('cliente', '')
    importe = float(payload.get('importe', 0) or 0)
    usdt = float(payload.get('usdt', 0) or 0)
    estado = payload.get('estado', '')
    tipo = payload.get('tipo', '')
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            UPDATE operaciones
            SET cliente = ?, importe = ?, usdt = ?, estado = ?, tipo = ?
            WHERE id = ?
        """, (cliente, importe, usdt, estado, tipo, op_id))
        conn.commit()
    return jsonify({"message": f"Operación {op_id} actualizada"}), 200

# API: eliminar (marcar como eliminada)
@app.route('/api/operaciones/<int:op_id>', methods=['DELETE'])
def api_delete_operacion(op_id):
    # por seguridad, marcamos como Eliminada (no borrado físico)
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("UPDATE operaciones SET estado = ? WHERE id = ?", ("Eliminada", op_id))
        conn.commit()
    return jsonify({"message": f"Operación {op_id} marcada como eliminada"}), 200

# Backup export
@app.route('/api/backup/export', methods=['GET'])
def api_backup_export():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM operaciones")
        rows = c.fetchall()
    return jsonify([list(r) for r in rows])

# Backup import (recibe json con key 'operaciones' = lista de filas tipo dict)
@app.route('/api/backup/import', methods=['POST'])
def api_backup_import():
    payload = request.json or {}
    ops = payload.get('operaciones', [])
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        for op in ops:
            c.execute(
                "INSERT INTO operaciones (tipo, cliente, importe, usdt, fecha, estado) VALUES (?, ?, ?, ?, ?, ?)",
                (op.get('tipo',''), op.get('cliente',''), float(op.get('importe',0) or 0), float(op.get('usdt',0) or 0), op.get('fecha', datetime.now().strftime("%Y-%m-%d %H:%M:%S")), op.get('estado','Finalizada'))
            )
        conn.commit()
    return jsonify({"message": "Backup importado"}), 200

# service worker & manifest
@app.route('/manifest.json')
def manifest():
    return send_from_directory('.', 'manifest.json')

@app.route('/service-worker.js')
def sw():
    return send_from_directory('.', 'service-worker.js')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
