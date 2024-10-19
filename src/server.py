import socket
import threading
import os


PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)


if not os.path.exists("./chat_logs"):
    os.makedirs("./chat_logs")


clients = {}
clients_count = 0
active_clients = 0



def handle_client(client_socket, client_id):
    global clients, active_clients
    print(f"[NEW CONNECTIONS] {client_id} connected.")
    file_path_log = f"./chat_logs/client_{client_id}_chat_log.txt"

    while True:
        massage = client_socket.recv(1024).decode("utf-8")
        if massage:
            if massage.lower() == "finish":
                client_socket.send("chat ended. now you can exit.".encode("utf-8"))
                break
            else:
                log_chat(file_path_log, f"Client[{client_id}] : {massage}")
                broadcast(f"Client[{client_id}] : {massage}", client_id)
        else:
            break

    client_socket.close()
    del clients[client_id]
    active_clients -= 1
    print(f"Client[{client_id}] disconnected. Active Clients : {active_clients}")

    if active_clients == 0:
        print("No active client. Closing server...")
        shutdown_server()


def broadcast(massage, sender_id):
    for clients_id, client_socket in clients.items():
        if clients_id != sender_id:
            client_socket.send(massage.encode("utf-8"))

def log_chat(file_path_log, massage):
    with open(file_path_log, "a") as log_file:
        log_file.write(massage + "\n")

def shutdown_server():
    for client_socket in clients.values():
        client_socket.close()
        print("Server closed.")
        exit(0)

def start():
    global active_clients, clients_count, clients
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] server is listening on {SERVER}")

    while True:
        clinet_socket, client_addr = server.accept()
        clients_count += 1
        client_id = clients_count
        clients[client_id] = clinet_socket
        active_clients += 1

        print(f"[ACTIVE CONNECTIONS] connected from {client_addr} , assigned CLIENT_ID: {client_id}")
        thread = threading.Thread(target=handle_client, args=(clinet_socket, client_id))
        thread.start()



if __name__ == "__main__":
    print("[STARTING] server is starting...")
    start()