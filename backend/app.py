import psycopg2
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

# PostgreSQL connection details
DB_NAME = "vm_management"
DB_USER = "admin"
DB_PASSWORD = "secret"
DB_HOST = "postgres"
DB_PORT = "5432"

def get_db_connection():
    connection = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    return connection

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Проверяем, существует ли пользователь
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        connection.close()
        return jsonify({'message': 'User already exists'}), 400

    # Хешируем пароль перед сохранением
    hashed_password = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (%s, %s)",
        (username, hashed_password)
    )
    connection.commit()
    connection.close()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    connection.close()

    if not user or not check_password_hash(user[1], password):
        return jsonify({'message': 'Invalid username or password'}), 400

    return jsonify({'message': 'Login successful', 'user_id': user[0]}), 200

@app.route('/vm', methods=['POST'])
def create_vm():
    data = request.json
    name = data.get('name')
    cpu = data.get('cpu')
    ram = data.get('ram')
    disk = data.get('disk')
    user_id = data.get('user_id')

    if not all([name, cpu, ram, disk, user_id]):
        return jsonify({'message': 'Missing fields'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO virtual_machines (name, cpu, ram, disk, user_id) VALUES (%s, %s, %s, %s, %s)",
        (name, cpu, ram, disk, user_id)
    )
    connection.commit()
    connection.close()

    return jsonify({'message': 'VM created successfully'}), 201

@app.route('/vm', methods=['GET'])
def list_vms():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({'message': 'Missing user_id'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, name, cpu, ram, disk FROM virtual_machines WHERE user_id = %s", (user_id,))
    vms = cursor.fetchall()
    connection.close()

    return jsonify([
        {
            'id': vm[0],
            'name': vm[1],
            'cpu': vm[2],
            'ram': vm[3],
            'disk': vm[4]
        } for vm in vms
    ]), 200

@app.route('/vm/<int:vm_id>', methods=['DELETE'])
def delete_vm(vm_id):
    print(f"Received DELETE request for VM ID: {vm_id}")
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM virtual_machines WHERE id = %s", (vm_id,))
    if cursor.rowcount == 0:
        connection.close()
        return jsonify({'message': 'VM not found'}), 404

    connection.commit()
    connection.close()

    return jsonify({'message': 'VM deleted successfully'}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
