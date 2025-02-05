import socket
import threading
import traceback
from backend import ft_event

from backend.protocols import PROTO


class ClientFileTransferManager:
    def __init__(
        self,
        client_socket: socket.socket,
        receive=False,
    ):
        self.client_socket = client_socket
        self.client_ft_socket = None
        self.receive = receive
        self.rec_lock = threading.Lock()

    def __enter__(self):
        self.client_ft_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.receive:
            return self.receive_mode()

        return self.send_mode()

    def __exit__(self, exc_type, exc_value, traceback):
        # if self.client_ft_socket and not self.receive:
        #     self.client_ft_socket.close()
        pass

    def receive_mode(self):
        try:
            protocol = self.client_socket.recv(10).decode().strip()

            if protocol != PROTO.FTRAN_P0RT:
                return None

            ft_port = int(self.client_socket.recv(6).decode().strip())
            print("Port for connection to server receiver:", ft_port)

            if not ft_port:
                return None

            self.client_ft_socket.connect(("", ft_port))
            print("Successfully connected, client to sender port:", ft_port)

            protocol = self.get_received_data(10).decode().strip()
            print("PROTO: ", protocol)

            if protocol != PROTO.FILE:
                return None

            username_length = self.get_received_length()
            print("Username length:", username_length)
            encrypted_username = self.get_received_data(username_length)
            print("Username:", encrypted_username)
            filename_length = self.get_received_length()
            print("Filename length:", filename_length)
            encrypted_filename = self.get_received_data(filename_length)
            print("Filename:", encrypted_filename)
            file_size = int(self.get_received_data(10).decode().strip())
            print("File size:", file_size)

            # print("Username:", encrypted_username)
            # print("Filename:", encrypted_filename)
            # print("File size:", file_size)

            return (
                self.client_ft_socket,
                encrypted_username,
                encrypted_filename,
                file_size,
            )
        except Exception as e:
            print(e)

    def send_mode(self):
        print(f"ft_event ID in ClientFTManager: {id(ft_event)}")
        protocol = PROTO.FT_REQUEST

        self.client_socket.sendall(f"{protocol.ljust(10)}".encode())
        # ready_status = server

        # here error occurring
        self.rec_lock.acquire()
        receive = self.client_socket.recv(16)  # client socket in None

        protocol = receive[:10].decode().strip()
        print("Protocol client:", protocol)
        self.rec_lock.release()

        if protocol != PROTO.FTRAN_P0RT:
            print("Protocol not supported")
            return

        ft_port = int(receive[10:].decode().strip())
        print("Port for connection to server receiver:", ft_port)
        try:
            self.client_ft_socket.connect(("", ft_port))
            print("Successfully connected.")
            return self.client_ft_socket
        except socket.error as e:
            print(e)
            traceback.print_exc()

    def get_received_length(self):
        return int(self.client_ft_socket.recv(4).decode().strip())

    def get_received_data(self, length):
        return self.client_ft_socket.recv(length)

    def cleanup(self):
        self.client_ft_socket.close()
