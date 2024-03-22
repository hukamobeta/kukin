import socket
import logging
from threading import Thread

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', filename='server.log', filemode='a')

class UDPServer:
    def __init__(self, host='127.0.0.1', port=12345):
        self.host = host
        self.port = port
        self.clients = set()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))
        logging.info(f"UDP чат-сервер слушает {self.host}:{self.port}")

    def broadcast_message(self, message, origin):
        for client in self.clients:
            if client != origin:
                self.server_socket.sendto(message, client)
                logging.info(f"Сообщение рассылается клиенту {client}")

    def handle_client(self):
        while True:
            message, client_address = self.server_socket.recvfrom(4096)
            logging.info(f"Получено сообщение от {client_address}: {message.decode()}")
            if client_address not in self.clients:
                self.clients.add(client_address)
            self.broadcast_message(message, client_address)

    def run(self):
        try:
            Thread(target=self.handle_client, daemon=True).start()
            while True:
                pass
        except KeyboardInterrupt:
            logging.info("Сервер останавливается.")
            self.server_socket.close()

server = UDPServer()
server.run()
