import os
import sys
import socket
import threading
import logging
import logging.handlers
import json


project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from config import Config
import helpers
from helpers import project_root

LOG_DIR = os.path.join(project_root, 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def setup_logger(name, log_file, level=logging.INFO):
    handler = logging.handlers.RotatingFileHandler(os.path.join(LOG_DIR, log_file), maxBytes=5*1024*1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

connection_logger = setup_logger('connection', 'connection.log')
operation_logger = setup_logger('operation', 'operation.log')

if not os.path.exists(Config.DIRECTORY):
    os.makedirs(Config.DIRECTORY)

def authenticate(sock):
    user_credentials = helpers.load_user_credentials()
    sock.send("Введите логин: ".encode('utf-8'))
    login = sock.recv(1024).decode('utf-8').strip()
    sock.send("Введите пароль: ".encode('utf-8'))
    password = sock.recv(1024).decode('utf-8').strip()
    user_info = user_credentials.get(login, {})
    if user_info.get("password") == password:
        connection_logger.info(f'Авторизация успешна: {login}')
        sock.send("Авторизация успешна.\n".encode('utf-8'))
        user_dir = os.path.join(Config.DIRECTORY, login)
        return login, user_dir, user_info.get("role") == "admin"
    else:
        sock.send("Неверный логин или пароль.\n".encode('utf-8'))
        connection_logger.warning(f'Неудачная попытка авторизации: {login}')
        return None, False, False

def register_user(sock):
    user_credentials = helpers.load_user_credentials()
    sock.send("Выберите логин: ".encode('utf-8'))
    login = sock.recv(1024).decode('utf-8').strip()
    if login in user_credentials:
        sock.send("Пользователь с таким логином уже существует.\n".encode('utf-8'))
        return None, False
    sock.send("Выберите пароль: ".encode('utf-8'))
    password = sock.recv(1024).decode('utf-8').strip()
    default_quota = 104857600
    user_credentials[login] = {"password": password, "quota": default_quota, "used": 0, "role": "user"}
    helpers.save_user_credentials(user_credentials)
    user_dir = os.path.join(Config.DIRECTORY, login)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    sock.send("Регистрация успешна. Теперь вы можете войти.\n".encode('utf-8'))
    return login, False

def handle_client(client_socket):
    with client_socket as sock:
        address = sock.getpeername()
        connection_logger.info(f'Клиент подключен: {address}')

        try:
            sock.send("Добро пожаловать на FTP сервер!\n Выберите действие: 1. Регистрация 2. Вход\n".encode('utf-8'))
            while True:
                choice = sock.recv(1024).decode('utf-8').strip()
                connection_logger.info(f'Выбор клиента: {choice}')

                if choice == '1':
                    login, user_dir, isAdmin = register_user(sock)
                elif choice == '2':
                    login, user_dir, isAdmin = authenticate(sock)
                else:
                    sock.send("Неверный выбор. Попробуйте снова.\n".encode('utf-8'))
                    continue
                if login:
                    break
            while True:
                command_data = sock.recv(1024).decode('utf-8').strip()
                if not command_data:
                    break

                command, *args = command_data.split()
                flags = [arg for arg in args if arg.startswith('-')]
                non_flag_args = [arg for arg in args if not arg.startswith('-')]
                
                response = "Команда не реализована.\n"
                if command.lower() in Config.COMMANDS:
                    func_name = Config.COMMANDS[command.lower()]
                    func = getattr(helpers, func_name, None)
                    if func:
                        response = func(current_dir=user_dir, login=login, is_admin=isAdmin, flags=flags, args=non_flag_args)
                
                elif command == 'upload':
                    file_name = args[0] if args else None
                    if not file_name:
                        sock.sendall("Не указано имя файла.\n".encode('utf-8'))
                        continue
                    sock.sendall("Ready".encode('utf-8'))
                    file_content = sock.recv(1024)
                    response = helpers.upload(file_name, file_content, current_dir=user_dir)
                    sock.sendall(f"{response}\n".encode('utf-8'))

                elif command == 'download':
                    file_name = args[0] if args else None
                    if not file_name:
                        sock.sendall("Не указано имя файла.\n".encode('utf-8'))
                        continue
                    response, file_content = helpers.download(file_name, current_dir=user_dir)
                    if file_content:
                        sock.sendall(file_content)
                    else:
                        sock.sendall(f"{response}\n".encode('utf-8'))
                else:
                    response = "Команда не реализована.\n"
                sock.sendall(f"\nОтвет:\n{response}\n".encode('utf-8'))

        except ConnectionResetError:
            connection_logger.error(f'Соединение неожиданно оборвалось: {address}')
        except BrokenPipeError:
            connection_logger.error(f'Попытка записи в разорванное соединение: {address}')
        except Exception as e:
            connection_logger.error(f'Ошибка: {e} для {address}')
        finally:
            connection_logger.info(f'Клиент отключен: {address}')

def start_server(host='0.0.0.0', port=12345):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        connection_logger.info(f"Сервер запущен и слушает {host}:{port}")
        while True:
            client_socket, address = server_socket.accept()
            connection_logger.info(f"Подключение от {address}")
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.start()

start_server()
