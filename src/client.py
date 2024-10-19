import socket
import threading

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

def receive_message(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if message:
                print(message)
            else:
                break
        except:
            break

def start():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(ADDR)

    thread = threading.Thread(target=receive_message, args=(client_socket,))
    thread.start()

    print("Type 'finish' to end the chat.")
    while True:
        command = input()
        client_socket.send(command.encode("utf-8"))
        if command.lower() == "finish":
            break

    client_socket.close()

if __name__ == "__main__":
    start()
