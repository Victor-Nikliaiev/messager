from functools import wraps
import socket
import threading
from typing import List, Tuple

HOST = "0.0.0.0"
PORT = 1060
LISTENER_LIMIT = 5
active_clients: List[Tuple[str, socket.socket]] = []
message_lock = threading.Lock()
typing_lock = threading.Lock()
typing_users = set()


class PROTO:  # PROTOCOL
    ENTER_SERV = "ENTER_SERV"
    LEAVE_SERV = "LEAVE_SERV"
    USER_NAME = "USER_NAME"
    NO_TYPING = "NO_TYPING"
    SRV_DOWN = "SRV_DOWN"
    TYPING = "TYPING"
    FILE = "FILE"
    MSG = "MSG"
    EMPTY = ""


def debounce(wait_time):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if hasattr(wrapper, "_timer") and wrapper._timer is not None:
                wrapper._timer.cancel()

            def call_func():
                func(*args, **kwargs)

            wrapper._timer = threading.Timer(wait_time, call_func)
            wrapper._timer.start()

        return wrapper

    return decorator


def listen_for_messages(client_socket: socket.socket, username):
    while True:
        header = client_socket.recv(10).decode().strip()

        if header == PROTO.EMPTY:
            client_socket.close()
            active_clients.remove((username, client_socket))
            broadcast_service_message(PROTO.LEAVE_SERV, username)
            broadcast_message("SERVER", f"{username} left the chat.")
            print(f"{username} left the chat.")
            break

        if header == PROTO.MSG:
            message = receive_client_message(client_socket)
            broadcast_message(username, message)

        if header == PROTO.TYPING:
            typing_users.add(username)
            broadcast_service_message(header, username)
            handle_typing_status()

        if header == PROTO.FILE:
            forward_file_chunks(client_socket, username)


# def send_message_to_client(client_socket: socket.socket, message: str):
#     client_socket.sendall(message.encode())


def broadcast_message(sender_username, message):
    # Sending MSG protocol
    # Sending username length
    # Sending username
    # Sending message length
    # Sending message

    protocol = PROTO.MSG.ljust(10)

    message_length = len(message)
    message_length = f"{message_length:04}"

    sender_username_length = len(sender_username)
    sender_username_length = f"{sender_username_length:04}"

    protocol_payload = (
        f"{protocol}{sender_username_length}{sender_username}{message_length}"
    )

    for client in active_clients:
        user_socket = client[1]

        try:
            user_socket.sendall(protocol_payload.encode())
            user_socket.sendall(message.encode())
        except Exception as e:
            print(f"Failed to send message to client: {client[0]}")
            active_clients.remove(client)


def broadcast_service_message(header, username):
    # Send protocol
    # Send username length
    # Send username

    protocol = header.ljust(10)
    username_length = len(username)
    username_length = f"{username_length:04}"
    payload = f"{protocol}{username_length}{username}"

    for client in active_clients:
        user_socket = client[1]
        user_socket.sendall(payload)


def receive_client_message(client_socket):
    message_length = client_socket.recv(4).decode()
    if not message_length:
        return None

    message_length = int(message_length.strip())
    message = ""
    bytes_received = 0

    while bytes_received < message_length:
        chunk = client_socket.recv(min(2048, message_length - bytes_received))
        if not chunk:
            raise ConnectionError("Client disconnected during message transfer.")

        message += chunk.decode()
        bytes_received += len(chunk)

    return message


def forward_file_chunks(client_socket: socket.socket, username):
    filename_length = int(client_socket.recv(4).decode().strip())
    filename = client_socket.recv(filename_length).decode()
    file_size = int(client_socket.recv(10).decode().strip())

    file_payload = (
        f"{PROTO.FILE.ljust(10)}{filename_length:04}{filename}{file_size:010}"
    )
    broadcast_message("SERVER", f"{username} is sending a file: {filename}")

    for client in active_clients:
        user_socket = client[1]

        if user_socket == client_socket:  # Don't send back to the sender
            continue

        try:
            user_socket.sendall(file_payload.encode())
        except Exception as e:
            print("Error sending file payload: {e}")

    sent_size = 0

    while sent_size < file_size:
        # Receive a chunk from the sender
        chunk = client_socket.recv(min(4096, file_size - sent_size))

        if not chunk:
            break

        sent_size += len(chunk)

        # Relay the chunk to all clients
        for client in active_clients:
            user_socket = client[1]

            if user_socket == client_socket:  # Don't send back to the sender
                continue

            try:
                # client[1].send(b"FILE     ")
                # client[1].send(f"{len(filename):04}".encode())  # send filename length
                # client[1].send(filename.encode())

                user_socket.send(chunk)
            except Exception as e:
                print("Error sending file chunk: {e}")

    broadcast_message(
        "SERVER", f"{username} finished sending {filename}. Click the link to download."
    )


@debounce(1.0)
def handle_typing_status():
    while typing_users:
        username = typing_users.pop()
        broadcast_service_message("NO_TYPING", username)


def client_handler(client_socket: socket.socket):
    while True:
        header = client_socket.recv(10).decode().strip()

        if header == PROTO.EMPTY:
            client_socket.close()
            print("Client username was empty. Client has been disconnected.")
            return

        if header == PROTO.USER_NAME:
            username_length = int(client_socket.recv(4).decode().strip())
            username = client_socket.recv(username_length).decode().strip()

            if not username:
                return

            active_clients.append(username, client_socket)
            print(f"{username} joined in.")
            broadcast_message("SERVER", f"{username} have been added to the chat.")
            broadcast_service_message(PROTO.ENTER_SERV, username)
            break

    threading.Thread(
        target=listen_for_messages,
        args=(
            client_socket,
            username,
        ),
    ).start()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.bind((HOST, PORT))
        print(f"Running the server on host: {HOST}, port: {PORT}")
    except Exception as e:
        print(f"Unable to bind to host {HOST} and port {PORT}")
        print(e)

    server_socket.listen(LISTENER_LIMIT)

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(
                f"Successfully connected to client at host: {client_address[0]} and port:{client_address[1]} "
            )

            threading.Thread(target=client_handler, args=(client_socket,)).start()
    finally:
        broadcast_service_message(PROTO.SRV_DOWN, "SERVER")
        server_socket.close()


if __name__ == "__main__":
    main()
