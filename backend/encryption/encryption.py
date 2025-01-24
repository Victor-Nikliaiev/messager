from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os


class EncryptionManager:
    def __init__(self, aes=False):
        self.private_key, self.public_key = self.generate_rsa_keys()
        if aes:
            self.aes_key = self.generate_aes_key()

    # Generate RSA key pair
    def generate_rsa_keys(self):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
        public_key = private_key.public_key()
        return private_key, public_key

    def generate_aes_key(self):
        return os.urandom(32)

    # Encrypt AES key with RSA public key
    def encrypt_aes_key(self, aes_key, public_key) -> bytes:
        encrypted_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return encrypted_key

    # Decrypt AES key with RSA private key
    def decrypt_aes_key(self, encrypted_key, private_key):
        decrypted_key = private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return decrypted_key

    # Encrypt message with AES-GCM
    def encrypt_message(self, message, aes_key):
        iv = os.urandom(12)  # 12 bytes IV for GCM
        cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(message.encode()) + encryptor.finalize()
        return iv, encryptor.tag, ciphertext

    # Decrypt message with AES-GCM
    def decrypt_message(self, iv, tag, ciphertext, aes_key):
        cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()
        decrypted_message = decryptor.update(ciphertext) + decryptor.finalize()
        return decrypted_message.decode()

    ##### FILES #####

    def encrypt_file(self, input_file, output_file, aes_key, public_key):
        iv = os.urandom(12)  # 12-byte IV for AES-GCM
        cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv))
        encryptor = cipher.encryptor()

        with open(input_file, "rb") as f:
            plaintext = f.read()

        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        encrypted_aes_key = self.encrypt_aes_key(aes_key, public_key)

        with open(output_file, "wb") as f:
            f.write(encrypted_aes_key + iv + encryptor.tag + ciphertext)

        print("File encrypted successfully!")

    # Function to decrypt a file
    def decrypt_file(self, input_file, output_file, private_key):
        key_size = 512  # RSA-4096 key size in bytes (4096 bits = 512 bytes)

        with open(input_file, "rb") as f:
            encrypted_aes_key = f.read(key_size)
            iv = f.read(12)
            tag = f.read(16)
            ciphertext = f.read()

        aes_key = self.decrypt_aes_key(encrypted_aes_key, private_key)
        cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

        with open(output_file, "wb") as f:
            f.write(decrypted_data)

        print("File decrypted successfully!")

    def serialize_private_key(self, private_key: rsa.RSAPrivateKey) -> bytes:
        return private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

    def serialize_public_key(self, public_key: rsa.RSAPublicKey) -> bytes:
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def deserialize_private_key(self, private_key_bytes: bytes) -> rsa.RSAPrivateKey:
        return serialization.load_pem_private_key(private_key_bytes, password=None)

    def deserialize_public_key(self, public_key_bytes: bytes) -> rsa.RSAPublicKey:
        return serialization.load_pem_public_key(public_key_bytes)


if __name__ == "__main__":
    em = EncryptionManager()
    # Example usage
    private_key, public_key = em.generate_rsa_keys()
    message = "Hello, this is a secret message!"

    # Generate random 32-byte AES key
    aes_key = os.urandom(32)

    # Encrypt the AES key using RSA
    encrypted_aes_key = em.encrypt_aes_key(aes_key, public_key)

    decrypted_aes_key = em.decrypt_aes_key(encrypted_aes_key, private_key)

    # Encrypt and decrypt message
    iv, tag, encrypted_message = em.encrypt_message(message, decrypted_aes_key)
    print("Encrypted message:", encrypted_message)
    decrypted_message = em.decrypt_message(
        iv, tag, encrypted_message, decrypted_aes_key
    )

    print("Original message:", message)
    print("Decrypted message:", decrypted_message)

if __name__ == "__main__":
    # Generate RSA keys
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    public_key = private_key.public_key()

    # Generate a random 32-byte AES key
    aes_key = os.urandom(32)

    # Example usage
    em.encrypt_file("input.txt", "encrypted_file.bin", aes_key, public_key)
    em.decrypt_file("encrypted_file.bin", "decrypted_output.txt", private_key)
