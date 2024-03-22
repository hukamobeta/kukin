import threading
import socket
import struct

class EnhancedSocket:
    def __init__(self, sock=None):
        if sock is None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.socket = sock
    
    def connect(self, address):
        self.socket.connect(address)

    def send_msg(self, msg):
        message_bytes = msg.encode()
        message_length = len(message_bytes)
        header = struct.pack('!I', message_length)
        self.socket.sendall(header + message_bytes)

    def recv_msg(self):
        header = self.socket.recv(4)
        if not header:
            return None
        message_length = struct.unpack('!I', header)[0]
        message = self.socket.recv(message_length).decode()
        return message

    def close(self):
        self.socket.close()

class ClientSocket(EnhancedSocket):
    def __init__(self, host, port):
        super().__init__()
        self.connect((host, port))
        self.listen_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
        self.listen_thread.start()

    def listen_for_messages(self):
        while True:
            message = self.recv_msg()
            if message is None:
                break
            print("\n" + message)

def get_server_details():
    host = input("Введите имя хоста [по умолчанию: 127.0.0.1]: ") or "127.0.0.1"
    port_input = input("Введите номер порта [по умолчанию: 9090]: ") or "9090"
    try:
        port = int(port_input)
    except ValueError:
        print("Некорректный ввод порта. Используется порт 9090.")
        port = 9090
    return host, port

def main():
    host, port = get_server_details()
    client_socket = ClientSocket(host, port)
    try:
        while True:
            msg = input()
            if msg.lower() == "exit":
                break
            client_socket.send_msg(msg)
    finally:
        client_socket.close()

main()