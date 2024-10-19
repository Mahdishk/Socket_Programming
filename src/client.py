import socket
import threading

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)


def recieve_massage(client_socket):
    while True:
        try:
            massage = client_socket.recv(1024).decode("utf-8")
            if massage:
                print(massage)
            else:
                break
        except:
            break


def start():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(ADDR)

    thread = threading.Thread(target=recieve_massage, args=(client_socket,))
    thread.start()

    print("Enter your massage or type 'finish' to end the chat.")
    while True:
        command = input()
        client_socket.send(command.encode("utf-8"))
        if command.lower() == "finish":
            break

    client_socket.close()


if __name__ == "__main__":
    start()