from functools import wraps
import socket
import threading
from typing import List, Tuple
import json
from concurrent.futures import ThreadPoolExecutor
from backend import PROTO
from backend import CONSTS


class Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.active_clients: List[Tuple[str, socket.socket]] = []
        self.typing_users = set()
        self.executor = ThreadPoolExecutor()

    def run(self):
        try:
            self.server_socket.bind((CONSTS.HOST, CONSTS.PORT))
            self.server_socket.listen(CONSTS.LISTENER_LIMIT)
            print(f"Running the server on host: {CONSTS.HOST}, port: {CONSTS.PORT}")

            while True:
                client_socket, client_address = self.server_socket.accept()
                print(
                    f"Successfully connected to client at host: {client_address[0]} and port:{client_address[1]} "
                )

                self.executor.submit(self.client_handler, client_socket)
                # threading.Thread(
                #     target=self.client_handler, args=(client_socket,)
                # ).start()
        except Exception as e:
            print(f"Unable to bind to host {CONSTS.HOST} and port {CONSTS.PORT}")
            print(e)

        finally:
            self.broadcast_service_message(PROTO.SRV_DOWN, "SERVER")
            self.server_socket.close()

    def client_handler(self, client_socket: socket.socket):
        while True:
            protocol = client_socket.recv(10).decode().strip()

            if protocol == PROTO.EMPTY:
                client_socket.close()
                print("Client username was empty. Client has been disconnected.")
                return

            if protocol == PROTO.USER_NAME:
                username_length = int(client_socket.recv(4).decode().strip())
                username = client_socket.recv(username_length).decode().strip()

                if not username:
                    return

                self.active_clients.append((username, client_socket))
                active_clients_list = [client[0] for client in self.active_clients]
                print(f"{username} joined in.")
                self.broadcast_message(
                    "SERVER", f"{username} have been added to the chat."
                )
                self.broadcast_service_message(
                    PROTO.UPD_ULIST, json.dumps(active_clients_list)
                )
                break

        self.executor.submit(self.listen_for_messages, client_socket, username)
        # threading.Thread(
        #     target=self.listen_for_messages,
        #     args=(
        #         client_socket,
        #         username,
        #     ),
        # ).start()

    def listen_for_messages(self, client_socket: socket.socket, username):
        while True:
            protocol = client_socket.recv(10).decode().strip()

            if protocol == PROTO.EMPTY:
                client_socket.close()
                self.active_clients.remove((username, client_socket))
                active_clients_list = [client[0] for client in self.active_clients]
                self.broadcast_service_message(
                    PROTO.UPD_ULIST, json.dumps(active_clients_list)
                )
                self.broadcast_message("SERVER", f"{username} left the chat.")
                print(f"{username} left the chat.")
                break

            if protocol == PROTO.MSG:
                message = self.receive_client_message(client_socket)
                self.broadcast_message(username, message)

            if protocol == PROTO.TYPING:
                self.typing_users.add(username)
                self.broadcast_service_message(protocol, username)
                self.handle_typing_status()

            if protocol == PROTO.FILE:
                # threading.Thread(
                #     target=forward_file_chunks, args=(client_socket, username)
                # ).start()
                self.forward_file_chunks(client_socket, username)
            if protocol == PROTO.PRIV_MSG:
                receiver_name_length = self.receive_length(client_socket)
                receiver_name = self.receive_data(client_socket, receiver_name_length)
                message_length = self.receive_length(client_socket)
                message = self.receive_data(client_socket, message_length)

                active_clients_list = [client[0] for client in self.active_clients]

                if receiver_name not in active_clients_list:
                    self.send_private_message(
                        client_socket,
                        "SERVER",
                        username,
                        f"User '{receiver_name}' is not online. Aborted.",
                    )
                    continue

                receiver_socket = self.active_clients[
                    active_clients_list.index(receiver_name)
                ][1]

                self.send_private_message(
                    receiver_socket, username, receiver_name, message
                )
                self.send_private_message(
                    client_socket, username, receiver_name, message
                )

    @staticmethod
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

    def send_private_message(
        self,
        receiver_socket: socket.socket,
        sender_username: str,
        receiver: str,
        message: str,
    ):
        protocol = PROTO.MSG.ljust(10)
        sender_username_length = len(sender_username.encode())

        message = f"[DM@{receiver}]: {message}"
        message_length = len(message.encode())

        payload = (
            f"{protocol}{sender_username_length:04}{sender_username}{message_length:04}"
        )
        receiver_socket.sendall(payload.encode() + message.encode())

    def receive_length(self, client_socket: socket.socket):
        return int(client_socket.recv(4).decode().strip())

    def receive_data(self, client_socket: socket.socket, length: int):
        return client_socket.recv(length).decode().strip()

    def broadcast_message(self, sender_username, message):
        # Sending MSG protocol
        # Sending username length
        # Sending username
        # Sending message length
        # Sending message

        protocol = PROTO.MSG.ljust(10)

        message_length = len(message.encode())
        message_length = f"{message_length:04}"

        sender_username_length = len(sender_username.encode())
        sender_username_length = f"{sender_username_length:04}"

        protocol_payload = (
            f"{protocol}{sender_username_length}{sender_username}{message_length}"
        )

        for client in self.active_clients:
            user_socket = client[1]

            try:
                user_socket.sendall(protocol_payload.encode())
                user_socket.sendall(message.encode())
            except Exception as e:
                print(f"Failed to send message to client: {client[0]}")
                self.active_clients.remove(client)

    def broadcast_service_message(self, protocol, data):
        # Send protocol
        # Send data length
        # Send data

        protocol = protocol.ljust(10)
        data_length = len(data.encode())
        data_length = f"{data_length:04}"
        payload = f"{protocol}{data_length}{data}"

        for client in self.active_clients:
            user_socket = client[1]
            user_socket.sendall(payload.encode())

    def receive_client_message(self, client_socket):
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

    def forward_file_chunks(self, client_socket: socket.socket, username: str):
        filename_length = int(client_socket.recv(4).decode().strip())
        filename = client_socket.recv(filename_length).decode()
        print("Server: Received filename:", filename)
        file_size = int(client_socket.recv(10).decode().strip())

        username_size = len(username.encode())

        file_payload = f"{PROTO.FILE.ljust(10)}{username_size:04}{username}{filename_length:04}{filename}{file_size:010}"
        self.broadcast_message("SERVER", f"{username} is sending a file: {filename}...")

        for client in self.active_clients:
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
            for client in self.active_clients:
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
        self.send_private_message(
            client_socket, "SERVER", username, "Your file has been sent successfully."
        )

    @debounce(1.0)
    def handle_typing_status(self):
        while self.typing_users:
            username = self.typing_users.pop()
            self.broadcast_service_message(PROTO.NO_TYPING, username)


if __name__ == "__main__":
    server = Server()
    server.run()
