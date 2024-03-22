import socket

def send_request(host, port, request):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        sock.sendall(request.encode('utf-8'))
        response = sock.recv(1024).decode('utf-8')
    return response

def test_registration(host, port):
    username = "test_user"
    password = "test_pass"
    request = f"1\n{username}\n{password}\n"
    expected_response = "Регистрация успешна. Теперь вы можете войти."
    response = send_request(host, port, request)
    assert expected_response in response, "Ошибка регистрации пользователя"

def test_login(host, port, username, password):
    request = f"2\n{username}\n{password}\n"
    expected_response = "Авторизация успешна."
    response = send_request(host, port, request)
    assert expected_response in response, "Ошибка входа пользователя"

def test_unauthorized_action(host, port):
    request = "some_invalid_command\n"
    expected_response = "Неизвестная команда или команда не реализована"
    response = send_request(host, port, request)
    assert expected_response in response, "Некорректная обработка несуществующей команды"

def main():
    host = "127.0.0.1"
    port = 12345

    try:
        test_registration(host, port)
        print("Тест регистрации пройден успешно.")
    except AssertionError as e:
        print(f"Тест регистрации не пройден: {e}")
    try:
        test_login(host, port, "test_user", "test_pass")
        print("Тест входа пройден успешно.")
    except AssertionError as e:
        print(f"Тест входа не пройден: {e}")

    try:
        test_unauthorized_action(host, port)
        print("Тест на несуществующую команду пройден успешно.")
    except AssertionError as e:
        print(f"Тест на несуществующую команду не пройден: {e}")

if __name__ == "__main__":
    main()
