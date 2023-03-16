# Name: Andrew Kim
# Pawprint: AHKYQX
# Date: 3/14/2023
# Description: Implements server side of a chatroom. Facilitates communication between multiple clients, including login, newuser, send, and logout functions.


import socket
import threading
import sys

bufsize = 1024  # Max amount of data to be received at once
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


# Handle client connections
def client_thread(conn, addr):
    conn.send(b"Welcome to the chatroom!")

    while True:
        try:
            # Receive data
            data = conn.recv(bufsize)
            if data:
                broadcast(data, conn)
            else:
                raise socket.error("Client disconnected")  # No data received
        except socket.error as err:
            # Client disconnected, remove from client_list
            remove(conn)
            print("Client disconnected:", err)
            conn.close()
            return


# Broadcast data to all connected clients
def broadcast(data, connection):
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
    if connection in client_list:
        connection.shutdown(socket.SHUT_RDWR)  # Shut down the socket
        connection.close()
        client_list.remove(connection)


# Accept client connections
print("Waiting for a client to connect...\n")
try:
    while True:
        conn, addr = server_socket.accept()

        if client_list.count(conn) < MAXCLIENTS:
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
