import socket
from backend.encryption import EncryptionManager
from backend.protocols import PROTO


class HeaderReceiver:
    def __init__(
        self,
        sender: tuple,
        em: EncryptionManager,
        sender_username: str,
    ):
        self.sender = sender
        self.sender_socket: socket.socket = sender[0]
        self.sender_aes = sender[1]
        self.sender_username = sender_username
        self.em = em
        print("Inside of header receiver")

    def __enter__(self):

        try:
            self.sender_socket.sendall(PROTO.SV_READY.ljust(10).encode())

            protocol = self.sender_socket.recv(10).decode().strip()

            if protocol != PROTO.FILE:
                return None

            filename_length = int(self.sender_socket.recv(4).decode().strip())
            encrypted_filename = self.sender_socket.recv(filename_length)
            decrypted_filename = self.em.decrypt_text(
                encrypted_filename, self.sender_aes
            )
            file_size = int(self.sender_socket.recv(10).decode().strip())

            if not decrypted_filename or not file_size:
                raise Exception("No data got in a header receiver")

            return (decrypted_filename, file_size)
        except Exception as e:
            print(f"Error in HeaderReceiver: {e}")

    def __exit__(self, exc_type, exc_value, traceback):
        pass
