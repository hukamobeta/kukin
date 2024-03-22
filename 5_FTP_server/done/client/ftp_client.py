import os
import socket

def upload_file(sock, file_path):
    try:
        with open(file_path, "rb") as file:
            file_name = os.path.basename(file_path)
            file_content = file.read()
            sock.sendall(f"upload {file_name}".encode('utf-8'))
            sock.recv(1024)
            sock.sendall(file_content)
            print(sock.recv(1024).decode('utf-8'))
    except Exception as e:
        print(f"Ошибка при загрузке файла: {e}")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('localhost', 12345))
        
        welcome_response = sock.recv(1024).decode('utf-8')
        print("Ответ сервера:", welcome_response)
        
        while True:
            command = input("Введите команду: ")
            if command.lower().startswith('exit'):
                break
            elif command.lower().startswith('upload'):
                _, file_path = command.split(maxsplit=1)
                upload_file(sock, file_path)
                continue
            elif command.lower().startswith('download'):
                _, file_name = command.split(maxsplit=1)
                download_file(sock, file_name, os.getcwd())
                continue
            
            sock.sendall(command.encode('utf-8'))
            response = sock.recv(1024).decode('utf-8')
            print("Ответ сервера:", response)


def download_file(sock, file_name, save_path):
    try:
        sock.sendall(f"download {file_name}".encode('utf-8'))
        file_content = sock.recv(1024)
        with open(os.path.join(save_path, file_name), "wb") as file:
            file.write(file_content)
        print("Файл успешно скачан.")
    except Exception as e:
        print(f"Ошибка при скачивании файла: {e}")


main()
