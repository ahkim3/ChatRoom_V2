# Name: Andrew Kim
# Pawprint: AHKYQX
# Date: 3/14/2023
# Description: Implements server side of a chatroom. Facilitates communication between multiple clients, including login, newuser, send, and logout functions.


import socket
import threading
import sys

bufsize = 1024  # Max amount of data to be received at once
users_file = "users.txt"  # File to store user credentials
MAXCLIENTS = 3  # Max number of clients that can connect to the server

# Set server IP address and port number
host = "127.0.0.1"
port = 19347

# Create socket
try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as err:
    print("Socket creation failed:", err)
    sys.exit()

# Bind the socket
try:
    server_socket.bind((host, port))
except socket.error as err:
    print("Binding failed:", err)
    sys.exit()

server_socket.listen(MAXCLIENTS)

client_list = []  # Keeps track of connected clients
logged_in_users = {}  # Dictionary of logged in users, with their usernames as keys


# Handle client connections
def client_thread(conn, addr):
    conn.send(b"Welcome to the chatroom!")

    while True:
        try:
            # Receive data
            data = conn.recv(bufsize).decode().strip()
            if data:
                # Parse command and parameters
                parts = data.split()
                command = parts[0].lower()
                params = parts[1:]

                # Handle login command
                if command == "login":
                    username, password = params
                    try:
                        if is_valid_credentials(username, password):
                            logged_in_users[conn] = username
                            conn.send(b"login confirmed")
                            print(username, "login.")
                        else:
                            conn.send(
                                b"Denied. User name or password incorrect.")
                    except FileNotFoundError:
                        conn.send(
                            b"The users.txt file does not exist. Please create a newuser.")

                # Handle logout command
                elif command == "logout":
                    username = logged_in_users[conn]
                    print(username, "logout.")
                    conn.close()
                    remove(conn)
                    break

            else:
                raise socket.error("Client disconnected")  # No data received
        except socket.error as err:
            # Client disconnected, remove from client_list
            remove(conn)
            print("Client disconnected:", err)
            conn.close()
            return


# Check if user is logged in
def is_logged_in(client):
    return client in client_list and client in logged_in_users.values()


# Check if user credentials are valid
def is_valid_credentials(username, password):
    # Grab user credentials from file
    with open(users_file, "r") as f:
        data = [tuple(line.strip().replace("(", "").replace(")", "").split(", "))
                for line in f if len(line.strip().split(", ")) == 2]

    # Check for a match
    for user, passwd in data:
        if user == username and passwd == password:
            return True
    return False


# Send data to specific client
def send(data, connection, client):
    if client in client_list:
        if client != connection and client.fileno() != -1:
            try:
                client.send(data)
            except socket.error as err:
                print("Socket error:", err)
                client.close()
                remove(client)
    else:
        print("Client not found.")


# Send data to all connected clients
def send_all(data, connection):
    for client in client_list:
        if client != connection and client.fileno() != -1:
            try:
                client.send(data)
            except socket.error as err:
                print("Socket error:", err)
                client.close()
                remove(client)


# Remove a client from the list
def remove(connection):
    try:
        # Remove from logged_in_users
        if connection in logged_in_users:
            del logged_in_users[connection]

        # Remove from client_list
        if connection in client_list:
            # connection.shutdown(socket.SHUT_RDWR)  # Shut down the socket
            connection.close()
            client_list.remove(connection)
    except socket.error or OSError as err:
        print("Socket error:", err)


# Accept client connections
print("Waiting for a client to connect...\n")
try:
    while True:
        conn, addr = server_socket.accept()
        if len(client_list) < MAXCLIENTS:
            client_list.append(conn)  # Append the new client

            print("Client Connected.")

            # New thread to handle the client connection
            threading.Thread(target=client_thread, args=(conn, addr)).start()
        else:
            conn.send(b"Server is full.")
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()

except KeyboardInterrupt:
    print("\nClosing server...")
    for conn in client_list:
        remove(conn)
    server_socket.close()
    sys.exit()

except socket.error as err:
    print("Socket error:", err)
    sys.exit()
