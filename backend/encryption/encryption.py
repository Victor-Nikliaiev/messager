from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os


# Generate RSA key pair
def generate_rsa_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    public_key = private_key.public_key()
    return private_key, public_key


# Encrypt AES key with RSA public key
def encrypt_aes_key(aes_key, public_key):
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
def decrypt_aes_key(encrypted_key, private_key):
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
def encrypt_message(message, aes_key):
    iv = os.urandom(12)  # 12 bytes IV for GCM
    cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(message.encode()) + encryptor.finalize()
    return iv, encryptor.tag, ciphertext


# Decrypt message with AES-GCM
def decrypt_message(iv, tag, ciphertext, aes_key):
    cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv, tag))
    decryptor = cipher.decryptor()
    decrypted_message = decryptor.update(ciphertext) + decryptor.finalize()
    return decrypted_message.decode()


if __name__ == "__main__":

    # Example usage
    private_key, public_key = generate_rsa_keys()
    message = "Hello, this is a secret message!"

    # Generate random 32-byte AES key
    aes_key = os.urandom(32)

    # Encrypt the AES key using RSA
    encrypted_aes_key = encrypt_aes_key(aes_key, public_key)

    decrypted_aes_key = decrypt_aes_key(encrypted_aes_key, private_key)

    # Encrypt and decrypt message
    iv, tag, encrypted_message = encrypt_message(message, decrypted_aes_key)
    print("Encrypted message:", encrypted_message)
    decrypted_message = decrypt_message(iv, tag, encrypted_message, decrypted_aes_key)

    print("Original message:", message)
    print("Decrypted message:", decrypted_message)


##### FILES #####


def encrypt_file(input_file, output_file, aes_key, public_key):
    iv = os.urandom(12)  # 12-byte IV for AES-GCM
    cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv))
    encryptor = cipher.encryptor()

    with open(input_file, "rb") as f:
        plaintext = f.read()

    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    encrypted_aes_key = encrypt_aes_key(aes_key, public_key)

    with open(output_file, "wb") as f:
        f.write(encrypted_aes_key + iv + encryptor.tag + ciphertext)

    print("File encrypted successfully!")


# Function to decrypt a file
def decrypt_file(input_file, output_file, private_key):
    key_size = 512  # RSA-4096 key size in bytes (4096 bits = 512 bytes)

    with open(input_file, "rb") as f:
        encrypted_aes_key = f.read(key_size)
        iv = f.read(12)
        tag = f.read(16)
        ciphertext = f.read()

    aes_key = decrypt_aes_key(encrypted_aes_key, private_key)
    cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv, tag))
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

    with open(output_file, "wb") as f:
        f.write(decrypted_data)

    print("File decrypted successfully!")


if __name__ == "__main__":
    # Generate RSA keys
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    public_key = private_key.public_key()

    # Generate a random 32-byte AES key
    aes_key = os.urandom(32)

    # Example usage
    encrypt_file("input.txt", "encrypted_file.bin", aes_key, public_key)
    decrypt_file("encrypted_file.bin", "decrypted_output.txt", private_key)
