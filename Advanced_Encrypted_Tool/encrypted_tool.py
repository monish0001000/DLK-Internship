import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from getpass import getpass
import secrets

# Generate key
def generate_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),   # ✅ FIXED
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

# Encrypt file
def encrypt_file(filename, password):
    salt = secrets.token_bytes(16)
    key = generate_key(password, salt)
    iv = secrets.token_bytes(16)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    with open(filename, 'rb') as f:
        data = f.read()

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()

    encrypted = encryptor.update(padded_data) + encryptor.finalize()

    with open("encrypted.bin", 'wb') as f:
        f.write(salt + iv + encrypted)

    print("✅ File encrypted successfully!")

# Decrypt file
def decrypt_file(filename, password):
    with open(filename, 'rb') as f:
        salt = f.read(16)
        iv = f.read(16)
        encrypted_data = f.read()

    key = generate_key(password, salt)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()

    with open("decrypted.txt", 'wb') as f:
        f.write(decrypted)

    print("✅ File decrypted successfully!")

# Menu
def main():
    print("\n--- Advanced Encryption Tool (AES-256) ---")
    print("1. Encrypt File")
    print("2. Decrypt File")

    choice = input("Enter choice: ")

    if choice == "1":
        file = input("Enter file name: ")
        password = getpass("Enter password: ")
        encrypt_file(file, password)

    elif choice == "2":
        file = input("Enter encrypted file: ")
        password = getpass("Enter password: ")
        decrypt_file(file, password)

    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
