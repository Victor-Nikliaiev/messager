from functools import wraps
import socket
import threading
import time
from typing import List, Tuple

HOST = "0.0.0.0"
PORT = 1060
LISTENER_LIMIT = 5
active_clients: List[Tuple[str, socket.socket]] = []
message_lock = threading.Lock()
typing_lock = threading.Lock()
typing_users = set()


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

        message = client_socket.recv(2048).decode()

        with message_lock:
            if message != "":
                if message.startswith("**TYPING**"):
                    with typing_lock:
                        typing_users.add(username)

                    time.sleep(0.1)
                    broadcast("SERVER", f"**TYPING**{username}")
                    handle_typing_list()
                    continue

                with typing_lock:
                    if username in typing_users:
                        typing_users.remove(username)
                        broadcast("SERVER", f"**NO_TYPING**{username}")
                time.sleep(0.1)
                broadcast(username, message)
                print(f"[{username}]: {message}")
            else:
                client_socket.close()
                active_clients.remove((username, client_socket))
                username_list = [client[0] for client in active_clients]
                broadcast("SERVER", "**UPDATE_USER_LIST**" + str(username_list))
                time.sleep(0.1)
                broadcast("SERVER", f"{username} left the chat.")
                print(f"{username} left the chat.")
                return


def send_message_to_client(client_socket: socket.socket, message: str):
    client_socket.sendall(message.encode())


def broadcast(from_user, message: str):
    if message.startswith("**UPDATE_USER_LIST**"):
        final_msg = message
    elif message.startswith("**SERVER_SHUTDOWN**"):
        final_msg = message
    elif message.startswith("**TYPING**"):
        username = message.split("**TYPING**")[1]
        final_msg = f"**TYPING**{username}"
    elif message.startswith("**NO_TYPING**"):
        username = message.split("**NO_TYPING**")[1]
        final_msg = f"**NO_TYPING**{username}"
    else:
        final_msg = f"{from_user}~{message}"

    for _, client_socket in active_clients:
        send_message_to_client(client_socket, final_msg)


def client_handler(client_socket: socket.socket):
    while True:
        username = client_socket.recv(2048).decode()

        if username != "":
            active_clients.append((username, client_socket))
            print(f"{username} joined in.")
            broadcast("SERVER", f"{username} have been added to the chat.")

            time.sleep(0.1)
            username_list = [client[0] for client in active_clients]
            broadcast("SERVER", "**UPDATE_USER_LIST**" + str(username_list))
            break
        else:
            print("Client username was empty. Client has been disconnected.")
            client_socket.close()
            return

    threading.Thread(
        target=listen_for_messages,
        args=(
            client_socket,
            username,
        ),
    ).start()


@debounce(1.0)
def handle_typing_list():
    with typing_lock:
        while typing_users:
            user = typing_users.pop()
            time.sleep(0.1)
            broadcast("SERVER", f"**NO_TYPING**{user}")


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
        broadcast("SERVER", "**SERVER_SHUTDOWN**")
        server_socket.close()


if __name__ == "__main__":
    main()
