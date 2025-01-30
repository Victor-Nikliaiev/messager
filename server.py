from base64 import encode
from functools import wraps
import os
import socket
import threading
import time
from typing import List, Tuple
import json
from concurrent.futures import ThreadPoolExecutor
from backend import PROTO
from backend import CONSTS
from backend.encryption import EncryptionManager
from cryptography.hazmat.primitives.asymmetric import rsa

from backend.managers import HeaderReceiver
from backend.managers import ServerFileTransferManager


class Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.active_clients: List[
            Tuple[bytes, socket.socket, bytes, rsa.RSAPublicKey]
        ] = []
        self.typing_users = set()
        self.executor = ThreadPoolExecutor()
        self.em = EncryptionManager()
        self.lock = threading.Lock()

    def run(self):
        try:
            self.server_socket.bind((CONSTS.HOST, int(CONSTS.PORT)))
            print(f"Running the server on host: {CONSTS.HOST}, port: {CONSTS.PORT}")

            self.server_socket.listen(CONSTS.LISTENER_LIMIT)

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
        username = None
        public_key = None
        decrypted_aes_key = None

        while True:
            protocol = client_socket.recv(10).decode().strip()

            if protocol == PROTO.EMPTY:
                client_socket.close()
                print("Client username was empty. Client has been disconnected.")
                return

            if protocol == PROTO.PUB_KEY:
                public_key_length = int(client_socket.recv(4).decode().strip())
                public_key_bytes = client_socket.recv(public_key_length)

                if not public_key_bytes:
                    print("Public key is required.")
                    return

                public_key = self.em.deserialize_public_key(public_key_bytes)
                self.send_server_public_key_to_client(client_socket)

            if protocol == PROTO.AES_KEY:
                encrypted_aes_key_length = self.receive_length(client_socket)
                encrypted_aes_key = client_socket.recv(encrypted_aes_key_length)
                decrypted_aes_key = self.em.decrypt_aes_key(
                    encrypted_aes_key, self.em.private_key
                )

            if protocol == PROTO.USER_NAME:
                username_length = int(client_socket.recv(4).decode().strip())
                username = client_socket.recv(username_length)

                if not username:
                    return

                username = self.em.decrypt_text(username, decrypted_aes_key)
                username_encrypted = self.em.encrypt_text(username, self.em.aes_key)
                self.active_clients.append(
                    (username_encrypted, client_socket, decrypted_aes_key, public_key)
                )

                active_clients_list = [
                    (self.em.decrypt_text(client[0], self.em.aes_key))
                    for client in self.active_clients
                ]

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

    def get_client_from_list(self, user_socket: socket.socket):
        for client in self.active_clients:
            if client[1] is user_socket:
                return client

    def send_server_public_key_to_client(self, client_socket: socket.socket):
        protocol = PROTO.PUB_KEY
        public_key_bytes = self.em.serialize_public_key(self.em.public_key)
        public_key_length = len(public_key_bytes)

        payload = f"{protocol.ljust(10)}{public_key_length:04}"
        client_socket.sendall(payload.encode() + public_key_bytes)

    def listen_for_messages(self, client_socket: socket.socket, username):
        while True:
            protocol = client_socket.recv(10).decode().strip()

            if protocol == PROTO.EMPTY:
                client_socket.close()

                client = self.get_client_from_list(client_socket)
                self.active_clients.remove(client)

                active_clients_list = [
                    self.em.decrypt_text(client[0], self.em.aes_key)
                    for client in self.active_clients
                ]

                self.broadcast_service_message(
                    PROTO.UPD_ULIST, json.dumps(active_clients_list)
                )
                print(f"{username} left.")
                self.broadcast_message("SERVER", f"{username} left the chat.")
                break

            if protocol == PROTO.MSG:
                message = self.receive_client_message(client_socket)
                self.broadcast_message(username, message)

            if protocol == PROTO.TYPING:
                self.typing_users.add(self.em.encrypt_text(username, self.em.aes_key))
                self.broadcast_service_message(protocol, username)
                self.handle_typing_status()

            if protocol == PROTO.FT_REQUEST:
                file_transfer_manager = ServerFileTransferManager(
                    client_socket, self.active_clients
                )

                sender_file_socket, client_ft_sessions = file_transfer_manager.setup()

                self.executor.submit(
                    self.forward_file_chunks,
                    sender_file_socket,
                    client_socket,
                    client_ft_sessions,
                    username,
                    file_transfer_manager.cleanup,
                )
                # self.proceed_file_sending(
                #     sender_file_socket, client_ft_sessions, client_socket, username
                # )

                # self.forward_file_chunks(
                #     sender_file_socket, client_socket, client_ft_sessions, username
                # )

            if protocol == PROTO.PRIV_MSG:
                self.receive_private_message(client_socket, username)

    # def proceed_file_sending(
    #     self, sender_file_socket, client_ft_sessions, client_socket, username
    # ):
    #     self.executor.submit(
    #         self.forward_file_chunks,
    #         sender_file_socket,
    #         client_socket,
    #         client_ft_sessions,
    #         username,
    #     )

    def receive_private_message(self, client_socket: socket.socket, username: str):
        receiver_name_length = self.receive_length(client_socket)
        encrypted_receiver_name = self.receive_data(client_socket, receiver_name_length)

        message_length = self.receive_length(client_socket)
        encrypted_message = self.receive_data(client_socket, message_length)

        active_clients_list = [
            self.em.decrypt_text(client[0], self.em.aes_key)
            for client in self.active_clients
        ]

        sender = self.get_client_from_list(client_socket)
        sender_aes_key = sender[2]

        decrypted_receiver_name = self.em.decrypt_text(
            encrypted_receiver_name, sender_aes_key
        )

        if decrypted_receiver_name not in active_clients_list:
            self.send_private_message(
                client_socket,
                "SERVER",
                username,
                f"User '{decrypted_receiver_name}' is not online. Aborted.",
            )
            return

        receiver_socket = self.active_clients[
            active_clients_list.index(decrypted_receiver_name)
        ][1]

        decrypted_message = self.em.decrypt_text(encrypted_message, sender_aes_key)

        self.send_private_message(
            receiver_socket,
            username,
            decrypted_receiver_name,
            decrypted_message,
        )
        self.send_private_message(
            client_socket, username, decrypted_receiver_name, decrypted_message
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
        receiver_username: str,
        message: str,
    ):
        protocol = PROTO.MSG.ljust(10)
        receiver_aes = self.get_client_from_list(receiver_socket)[2]

        encrypted_sender_username = self.em.encrypt_text(sender_username, receiver_aes)
        sender_username_length = len(encrypted_sender_username)

        message = f"[DM@{receiver_username}]: {message}"

        encrypted_msg = self.em.encrypt_text(message, receiver_aes)
        encrypted_msg_length = len(encrypted_msg)

        payload = (
            protocol.encode()
            + f"{sender_username_length:04}".encode()
            + encrypted_sender_username
            + f"{encrypted_msg_length:04}".encode()
            + encrypted_msg
        )
        receiver_socket.sendall(payload)

    def receive_length(self, client_socket: socket.socket):
        return int(client_socket.recv(4).decode().strip())

    def receive_data(self, client_socket: socket.socket, length: int):
        return client_socket.recv(length)

    def broadcast_message(self, sender_username, message):
        # Sending MSG protocol
        # Sending username length
        # Sending username
        # Sending message length
        # Sending message

        protocol = PROTO.MSG.ljust(10).encode()

        for client in self.active_clients:
            user_socket = client[1]
            user_aes_key = client[2]

            encrypted_sender_name = self.em.encrypt_text(sender_username, user_aes_key)
            sender_name_length = f"{len(encrypted_sender_name):04}".encode()

            encrypted_message = self.em.encrypt_text(message, user_aes_key)
            message_length = f"{len(encrypted_message):04}".encode()

            protocol_payload = (
                protocol
                + sender_name_length
                + encrypted_sender_name
                + message_length
                + encrypted_message
            )

            try:
                user_socket.sendall(protocol_payload)
            except Exception:
                self.active_clients.remove(client)

    def broadcast_service_message(self, protocol: str, data: str):
        # Send protocol
        # Send data length
        # Send data

        protocol = protocol.ljust(10).encode()

        for client in self.active_clients:
            user_socket = client[1]
            user_aes_key = client[2]

            encrypted_data = self.em.encrypt_text(data, user_aes_key)

            data_length = f"{len(encrypted_data):04}".encode()
            payload = protocol + data_length + encrypted_data
            user_socket.sendall(payload)

    def receive_client_message(self, client_socket: socket.socket):

        message_length = client_socket.recv(4).decode()
        if not message_length:
            return None

        message_length = int(message_length.strip())
        message = b""
        bytes_received = 0

        while bytes_received < message_length:
            chunk = client_socket.recv(min(2048, message_length - bytes_received))
            if not chunk:
                raise ConnectionError("Client disconnected during message transfer.")

            message += chunk
            bytes_received += len(chunk)

        client_aes = self.get_client_from_list(client_socket)[2]
        decrypted_message = self.em.decrypt_text(message, client_aes)

        return decrypted_message

    # TODO: Client send file transfer request
    # TODO: FileTransferServerManager established a connection with client on file transfer socket
    # TODO: sender(client) send FILE PROTOCOL with data payload.
    # TODO: server create another socket to communicate with receivers and connects to them through ft socket
    # TODO: as server receive a chunk he decrypt, encrypt and send it back to clients
    def forward_file_chunks(
        self,
        sender_file_socket: socket.socket,
        sender_socket: socket.socket,
        client_ft_sessions: List[Tuple[socket.socket, bytes]],
        sender_username: str,
        cleanup,
    ):
        print("Server, sender username:", sender_username)
        print("Server, sender_socket:", sender_socket)
        print("Server, client_ft_sessions:", client_ft_sessions)

        sender = self.get_client_from_list(sender_socket)
        sender = (sender_file_socket, sender[2])

        print("Server, sender:", sender)
        print("Server, forward_file_chunks:", sender)
        header_receiver = HeaderReceiver(sender, self.em, sender_username)

        with header_receiver as hr:
            if hr:
                print("hr is true...")
                decrypted_filename, file_size = hr
            else:
                return

        self.broadcast_message(
            "SERVER", f"{sender_username} is sending a file: {decrypted_filename}..."
        )

        for client in client_ft_sessions:
            client_socket = client[0]
            client_aes = client[1]

            encrypted_username = self.em.encrypt_text(sender_username, client_aes)
            username_length = len(encrypted_username)

            encrypted_file_name = self.em.encrypt_text(decrypted_filename, client_aes)
            filename_length = len(encrypted_file_name)

            file_payload = (
                PROTO.FILE.ljust(10).encode()
                + f"{username_length:04}".encode()
                + encrypted_username
                + f"{filename_length:04}".encode()
                + encrypted_file_name
                + f"{file_size:010}".encode()
            )
            try:
                client_socket.sendall(file_payload)
            except Exception as e:
                print("Error sending file payload: {e}")

        sent_size = 0
        chunk_index = 0

        while sent_size < file_size:
            try:
                chunk = sender_file_socket.recv(CONSTS.ENCRYPTED_CHUNK_SIZE)

                if not chunk:
                    print("No chunk received, waiting...")
                    time.sleep(1)
                    continue

                # Decrypt, encrypt and relay the chunk to active clients
                for receiver in client_ft_sessions:
                    receiver_socket = receiver[0]

                    # sender = self.get_client_from_list(
                    #     sender_file_socket, client_ft_sessions
                    # )
                    sender_aes = sender[1]

                    decrypted_chunk = self.em.decrypt_file_chunk(chunk, sender_aes)
                    sender_file_socket.send(f"ACK{chunk_index:06}".encode())

                    receiver_aes = receiver[1]
                    encrypted_chunk = self.em.encrypt_file_chunk(
                        decrypted_chunk, receiver_aes
                    )
                    try:
                        receiver_socket.send(encrypted_chunk)
                    except Exception as e:
                        print(f"Error sending chunk to client: {e}")

                    sent_size += CONSTS.ORIGINAL_CHUNK_SIZE
                    chunk_index += 1
                    print(f"{sent_size}/{file_size}/{chunk_index} chunks forwarded")
            except Exception as e:
                print(f"Error receiving/sending file chunk: {e}")
                break

        self.send_private_message(
            sender_socket,
            "SERVER",
            sender_username,
            "Your file has been sent successfully.",
        )

        cleanup()

    @debounce(1.0)
    def handle_typing_status(self):
        while self.typing_users:
            encrypted_username = self.typing_users.pop()
            decrypted_username = self.em.decrypt_text(
                encrypted_username, self.em.aes_key
            )

            self.broadcast_service_message(PROTO.NO_TYPING, decrypted_username)


if __name__ == "__main__":
    server = Server()
    server.run()
