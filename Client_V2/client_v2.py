# Name: Andrew Kim
# Pawprint: AHKYQX
# Date: 3/14/2023
# Description: Implements client side of a chatroom. Facilitates communication between multiple clients, including login, newuser, send, and logout functions.


import socket
import threading
import sys

bufsize = 1024  # Max amount of data to be received at once

# Set server IP address and port number
host = "127.0.0.1"
port = 19347

# Create socket
try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except:
    print("Socket creation failed.")
    sys.exit()

# Connect to server
try:
    client_socket.connect((host, port))
except:
    print("Unable to connect to server.")
    sys.exit()

# User is not logged in by default
logged_in = False


def validate(data):
    try:
        # Parse command and parameters
        parts = data.split()
        params = parts[1:]

        # If user is not logged in, only allow login and newuser commands
        if not logged_in:
            if data.startswith("login") or data.startswith("newuser"):
                # Check if login command is used correctly
                if data.startswith("login"):
                    if len(params) != 2:
                        print("Invalid usage. Usage: login <username> <password>")
                        return False
                    return True

                # Check if newuser command is used correctly
                elif data.startswith("newuser"):
                    if len(params) != 2:
                        print("Invalid usage. Usage: newuser <username> <password>")
                        return False

                    username, password = params

                    if len(username) < 3 or len(username) > 32:
                        print(
                            "Invalid username length (must be between 3 and 32 characters).")
                        return False

                    if len(password) < 4 or len(password) > 8:
                        print(
                            "Invalid password length (must be between 4 and 8 characters).")
                        return False

                    if any(c.isspace() for c in username) or any(c.isspace() for c in password):
                        print("Username and password cannot contain spaces.")
                        return False

                    return True
            else:
                # Unavailable commands
                if data.startswith("send") or data.startswith("who") or data.startswith("logout"):
                    print("Denied. Please login first.")
                    return False
                else:
                    print("Invalid command.")
                    return False
        else:
            if data.startswith("send") or data.startswith("who") or data.startswith("logout"):
                # Check if send all command is used correctly
                if data.startswith("send all"):
                    if len(params) <= 0:
                        print("Invalid usage. Usage: send all <message>")
                        return False

                    message = ' '.join(params[1:])

                    if len(message) > 256 or len(message) < 1:
                        print(
                            "Invalid message length (must be between 1 and 256 characters).")
                        return False

                    return True

                # Check if send command is used correctly
                elif data.startswith("send"):
                    if len(params) < 2:
                        print("Invalid usage. Usage: send <username> <message>")
                        return False

                    username = params[0]
                    message = ' '.join(params[1:])

                    if len(message) > 256 or len(message) < 1:
                        print(
                            "Invalid message length (must be between 1 and 256 characters).")
                        return False

                    return True

                # Check if who command is used correctly
                elif data.startswith("who"):
                    if len(params) != 0:
                        print("Invalid usage. Usage: who")
                        return False

                    return True

                # Check if logout command is used correctly
                elif data.startswith("logout"):
                    client_socket.send(data.encode())
                    client_socket.close()
                    sys.exit()  # No need to return after
            else:
                if data.startswith("login") or data.startswith("newuser"):
                    print("Denied. Please logout first.")
                    return False
                else:
                    print("Invalid command.")
                    return False
    except KeyboardInterrupt:
        print("\nClosing client...")
        client_socket.close()
        sys.exit()


# Receive data from the server
def receive():
    while True:
        try:
            data = client_socket.recv(bufsize).decode()
            if not data:
                print("Server disconnected.")
                break

            if data == b"login confirmed" or data == "login confirmed":
                global logged_in
                logged_in = True

            print(data)
        except socket.error as err:
            print("Socket error:", err)
            client_socket.close()
            sys.exit()


# Send data to the server
def send():
    while True:
        try:
            data = input()

            # Validate input
            if validate(data):
                client_socket.send(data.encode())
            else:
                pass

        except KeyboardInterrupt:
            print("\nClosing client...")
            client_socket.close()
            sys.exit()
        except socket.error as err:
            print("Socket error:", err)
            client_socket.close()
            sys.exit()


# Start threads to send and receive data
send_thread = threading.Thread(target=send)
send_thread.daemon = True
send_thread.start()

receive_thread = threading.Thread(target=receive)
receive_thread.daemon = True
receive_thread.start()

# Check if threads are alive
try:
    while receive_thread.is_alive() and send_thread.is_alive():
        pass
except KeyboardInterrupt:
    print("\nClosing client...")
finally:
    client_socket.close()
    sys.exit()
