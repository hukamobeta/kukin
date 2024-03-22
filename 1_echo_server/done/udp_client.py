import socket
from threading import Thread
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', filename='client.log', filemode='a')

def listen_for_messages(sock):
    while True:
        message, _ = sock.recvfrom(4096)
        received_message = message.decode()
        logging.info(f"Новое сообщение: {received_message}")
        print(f"\nНовое сообщение: {received_message}\nВаше сообщение: ", end="")

def start_client(server_host='127.0.0.1', server_port=12345):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.bind(("", 0))
    server_address = (server_host, server_port)

    Thread(target=listen_for_messages, args=(client_socket,), daemon=True).start()

    print("Вы можете начать писать сообщения. Напишите 'exit', чтобы выйти.")
    while True:
        message = input("Ваше сообщение: ")
        if message.lower() == "exit":
            break
        client_socket.sendto(message.encode(), server_address)
        logging.info(f"Отправлено сообщение: {message}")

    client_socket.close()

start_client()
