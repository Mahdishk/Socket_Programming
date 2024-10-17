import socket
import threading


PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def handle_client(client_socket, client_addr):
    print(f"[NEW CONNECTIONS] {client_addr} connected.")

    while True:
        massage = client_socket.recv(1024).decode("utf-8")
        if massage:
            if massage.lower() == "finish":
                break
        else:
            break

        print(f"[{client_addr}] {massage}")

    client_socket.close()


def start():
    server.listen()
    print(f"[LISTENING] server is listening on {SERVER}")
    while True:
        clinet_socket, client_addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(clinet_socket, client_addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


if __name__ == "__main__":
    print("[STARTING] server is starting...")
    start()