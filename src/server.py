import socket
import threading
import os
import pandas as pd
import numpy as np  # Import numpy for array splitting
import random

# Load data from CSV
file_path = '/home/mahdi/Uni_Project/Socket_Programming/data/Randomdata.csv'
data = pd.read_csv(file_path)

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

clients = {}
clients_count = 0
active_clients = 0

# Global DataFrames
available_data = data.copy()
sent_data = {}  # Tracks rows sent to each client

# Directory to store client data files
if not os.path.exists("./client_data"):
    os.makedirs("./client_data")

def handle_client(client_socket, client_id):
    global clients, active_clients, available_data, sent_data
    
    print(f"[NEW CONNECTION] Client {client_id} connected.")
    client_sent_data = pd.DataFrame()
    client_file_path = f"./client_data/data_of_client_{client_id}.csv"

    if available_data.empty:
        client_socket.send("No more unique data available.".encode("utf-8"))
    else:
        # Send random rows of data between 2000 and 5000 to the client
        random_amount = random.randint(2000, 5000)  # Random number of rows to send
        if random_amount > len(available_data):
            random_amount = len(available_data)  # Adjust if we have fewer rows than requested

        client_sent_data = available_data.sample(n=random_amount)  # Sample data
        available_data = available_data.drop(client_sent_data.index)  # Remove the sent rows from available_data
        sent_data[client_id] = client_sent_data  # Track the data sent to this client

        # Save the sent data to a CSV file
        client_sent_data.to_csv(client_file_path, index=False)

        for _, row in client_sent_data.iterrows():
            message = f"{row.to_dict()}"
            client_socket.send(message.encode("utf-8"))

    # Wait for the "finish" command or disconnection
    try:
        while True:
            message = client_socket.recv(1024).decode("utf-8")
            if message:
                if message.lower() == "finish":
                    client_socket.send("Chat ended. Now you can exit.".encode("utf-8"))
                    break
                else:
                    print(f"Client[{client_id}] : {message}")
            else:
                break
    except ConnectionResetError:
        pass  # Handle unexpected disconnection
    
    # Handle disconnection
    client_socket.close()
    print(f"Client[{client_id}] disconnected.")

    # Redistribute the client's data to other active clients or return to pool
    if client_id in sent_data:
        redistribute_data(sent_data[client_id], client_id)
        del sent_data[client_id]  # Remove the client from sent_data

    # Remove the file associated with the client
    if os.path.exists(client_file_path):
        os.remove(client_file_path)
        print(f"File {client_file_path} deleted.")

    del clients[client_id]
    active_clients -= 1
    print(f"Active Clients: {active_clients}")

    if active_clients == 0:
        print("No active clients. Closing server...")
        shutdown_server()

def redistribute_data(data_to_redistribute, disconnected_client_id):
    """
    Redistribute the data of a disconnected client to other active clients
    and update their corresponding files.
    """
    # Check if there are other active clients to redistribute data
    active_client_ids = [client_id for client_id in clients if client_id != disconnected_client_id]
    
    if len(active_client_ids) == 0:
        print("No active clients to redistribute data. Returning data to available pool.")
        global available_data
        available_data = pd.concat([available_data, data_to_redistribute])  # Return data to the available pool
        return

    # Split the data equally among active clients
    split_data = np.array_split(data_to_redistribute, len(active_client_ids))
    
    for i, client_id in enumerate(active_client_ids):
        if not split_data[i].empty:
            # Send the data to the active client
            for _, row in split_data[i].iterrows():
                message = f"Redistributed data: {row.to_dict()}"
                clients[client_id].send(message.encode("utf-8"))
            
            # Track the redistributed data in the client's sent data
            if client_id in sent_data:
                sent_data[client_id] = pd.concat([sent_data[client_id], split_data[i]])
            else:
                sent_data[client_id] = split_data[i]
            
            # Update the client's file with the new data
            client_file_path = f"./client_data/data_of_client_{client_id}.csv"
            if os.path.exists(client_file_path):
                # Append to the existing file
                split_data[i].to_csv(client_file_path, mode='a', header=False, index=False)
            else:
                # Create a new file if it doesn't exist (unlikely, but for safety)
                split_data[i].to_csv(client_file_path, index=False)

    print(f"Data from Client[{disconnected_client_id}] redistributed to active clients and files updated.")

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
    print(f"[LISTENING] Server is listening on {SERVER}")

    while True:
        client_socket, client_addr = server.accept()
        clients_count += 1
        client_id = clients_count
        clients[client_id] = client_socket
        active_clients += 1

        print(f"[ACTIVE CONNECTIONS] Connected from {client_addr}, assigned CLIENT_ID: {client_id}")
        thread = threading.Thread(target=handle_client, args=(client_socket, client_id))
        thread.start()

if __name__ == "__main__":
    print("[STARTING] Server is starting...")
    start()
