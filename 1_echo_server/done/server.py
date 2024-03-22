import hashlib
import os
import json
import logging
import struct
import socket
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', filename='server.log', filemode='a')

class EnhancedSocket:
    def __init__(self, existing_socket=None):
        self.socket = existing_socket if existing_socket else socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def send_msg(self, msg):
        if isinstance(msg, str):
            msg = msg.encode()
        msg_length = len(msg)
        header = struct.pack('>I', msg_length)
        self.socket.sendall(header + msg)
    
    def recv_msg(self):
        header = self.socket.recv(4)
        if not header:
            return ""
        msg_length = struct.unpack('>I', header)[0]
        msg = self.socket.recv(msg_length)
        return msg.decode()
    
    def accept(self):
        conn, addr = self.socket.accept()
        return EnhancedSocket(conn), addr
    
    def close(self):
        self.socket.close()
    
    def bind(self, address):
        self.socket.bind(address)
    
    def listen(self, backlog):
        self.socket.listen(backlog)
    
    def connect(self, address):
        self.socket.connect(address)

def hash_password(password):
    """Возвращает хеш пароля."""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token():
    """Генерирует случайный токен сессии."""
    return os.urandom(16).hex()

def load_users_db(filename="users_db.json"):
    """Загружает базу данных пользователей из файла JSON."""
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_users_db(filename, users_db):
    """Сохраняет базу данных пользователей в файл JSON."""
    with open(filename, "w") as file:
        json.dump(users_db, file, indent=4)

active_connections = []

def broadcast_message(sender_conn, message):
    for conn in active_connections:
        if conn is not sender_conn:
            conn.send_msg(message)

def handle_connection(conn, users_db):
    active_connections.append(conn)
    try:
        conn.send_msg("Введите имя пользователя:")
        username = conn.recv_msg()
        conn.send_msg("Введите пароль:")
        password = conn.recv_msg()
        hashed_password = hash_password(password)

        if username in users_db and users_db[username]["password"] == hashed_password:
            token = generate_token()
            users_db[username]["token"] = token
            save_users_db("users_db.json", users_db)
            conn.send_msg(f"Вы успешно аутентифицированы. Ваш токен: {token}")
        elif username not in users_db:
            token = generate_token()
            users_db[username] = {"password": hashed_password, "token": token}
            save_users_db("users_db.json", users_db)
            conn.send_msg(f"Пользователь создан и успешно аутентифицирован. Ваш токен: {token}")
        else:
            conn.send_msg("Неверный пароль. Попробуйте снова.")
        
        while True:
            message = conn.recv_msg()
            if message is None or message.lower() == 'exit':
                break
            broadcast_message(conn, message)
    finally:
        active_connections.remove(conn)
        conn.close()

def main():
    users_db = load_users_db("users_db.json")
    server_socket = EnhancedSocket()
    server_socket.bind(('', 0))
    server_socket.listen(1)
    port = server_socket.socket.getsockname()[1]
    logging.info(f"Сервер слушает порт {port}")

    try:
        while True:
            conn, addr = server_socket.accept()
            logging.info(f"Подключен {addr}")
            threading.Thread(target=handle_connection, args=(conn, users_db), daemon=True).start()
    finally:
        server_socket.close()

main()
