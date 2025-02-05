import socket
from typing import List, Tuple

from backend import PROTO
from cryptography.hazmat.primitives.asymmetric import rsa


class ServerFileTransferManager:
    def __init__(
        self,
        sender_socket: socket.socket,
        active_clients: List[Tuple[bytes, socket.socket, bytes, rsa.RSAPublicKey]],
    ):
        self.sender_socket = sender_socket
        self.server_file_socket_receiver = None
        self.server_file_socket_sender = None
        self.sender_file_socket = None
        self.transfer_port = None
        self.active_clients = active_clients
        self.client_ft_sessions: List[Tuple[socket.socket, bytes]] = []

    def setup(self):
        self.server_file_socket_receiver = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        self.server_file_socket_receiver.bind(("", 0))
        self.server_file_socket_receiver.listen(1)
        self.transfer_port = self.server_file_socket_receiver.getsockname()[1]
        payload = f"{PROTO.FTRAN_P0RT.ljust(10)}{self.transfer_port:06}"

        try:
            self.sender_socket.sendall(payload.encode())
            self.sender_file_socket, _ = self.server_file_socket_receiver.accept()
            print(
                "FileTransferServerManager: Sender connected to server ft-receiver socket."
            )

            self.get_client_ft_sockets()
        except Exception as e:
            print(e)

        return self.sender_file_socket, self.client_ft_sessions

        # def __exit__(self, exc_type, exc_value, traceback):
        # if self.sender_file_socket:
        #     self.sender_file_socket.close()
        # if self.server_file_socket_receiver:
        #     self.server_file_socket_receiver.close()
        # if self.server_file_socket_sender:
        #     self.server_file_socket_sender.close()

        # for ft_socket, _ in self.client_ft_sessions:
        #     ft_socket.close()

        # self.client_ft_sessions.clear()
        # pass

    def get_client_ft_sockets(self):
        self.transfer_port = None
        self.server_file_socket_sender = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        self.server_file_socket_sender.bind(("", 0))
        self.server_file_socket_sender.listen()

        for client in self.active_clients:
            client_socket = client[1]

            if client_socket is self.sender_socket:
                continue

            protocol = PROTO.FT_REQUEST
            client_socket.send(f"{protocol.ljust(10)}".encode())

            self.transfer_port = self.server_file_socket_sender.getsockname()[1]
            protocol = PROTO.FTRAN_P0RT
            payload = f"{protocol.ljust(10)}{self.transfer_port:06}"

            client_socket.send(payload.encode())

            client_ft_socket, _ = self.server_file_socket_sender.accept()
            print(
                "FileTransferServerManager: client connected to server ft-sender socket."
            )

            client_aes_key = client[2]
            self.client_ft_sessions.append((client_ft_socket, client_aes_key))

    def cleanup(self):
        if self.sender_file_socket:
            self.sender_file_socket.close()
        if self.server_file_socket_receiver:
            self.server_file_socket_receiver.close()
        if self.server_file_socket_sender:
            self.server_file_socket_sender.close()

        for ft_socket, _ in self.client_ft_sessions:
            ft_socket.close()

        self.client_ft_sessions.clear()
