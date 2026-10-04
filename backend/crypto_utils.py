import os
import struct
import hmac
import hashlib

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


# ============================================================
# SECURITY SETTINGS
# ============================================================

MAGIC = b"FPU1"
SALT_SIZE = 16
IV_SIZE = 16
KEY_SIZE = 32
MAC_SIZE = 32

# PBKDF2 iterations
PBKDF2_ITERATIONS = 600_000

BLOCK_SIZE = 16


# ============================================================
# KEY DERIVATION
# ============================================================

def derive_keys(password: str, salt: bytes):
    """
    Derive two 256-bit keys from the password:
    - encryption key
    - HMAC authentication key
    """

    if not password:
        raise ValueError("Password cannot be empty.")

    password_bytes = password.encode("utf-8")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=64,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )

    derived_key = kdf.derive(password_bytes)

    encryption_key = derived_key[:32]
    mac_key = derived_key[32:]

    return encryption_key, mac_key


# ============================================================
# PKCS7 PADDING
# ============================================================

def add_padding(data: bytes):
    padding_length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)

    padding = bytes([padding_length]) * padding_length

    return data + padding


def remove_padding(data: bytes):
    if not data:
        raise ValueError("Invalid encrypted data.")

    padding_length = data[-1]

    if padding_length < 1 or padding_length > BLOCK_SIZE:
        raise ValueError("Invalid padding.")

    if data[-padding_length:] != bytes([padding_length]) * padding_length:
        raise ValueError("Invalid padding.")

    return data[:-padding_length]


# ============================================================
# AES-256-CBC ENCRYPTION
# ============================================================

def aes_encrypt(data: bytes, key: bytes, iv: bytes):
    padded_data = add_padding(data)

    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv)
    )

    encryptor = cipher.encryptor()

    return encryptor.update(padded_data) + encryptor.finalize()


# ============================================================
# AES-256-CBC DECRYPTION
# ============================================================

def aes_decrypt(ciphertext: bytes, key: bytes, iv: bytes):
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv)
    )

    decryptor = cipher.decryptor()

    padded_data = decryptor.update(ciphertext) + decryptor.finalize()

    return remove_padding(padded_data)


# ============================================================
# FILE ENCRYPTION
# ============================================================

def encrypt_file(input_path: str, output_path: str, password: str):
    """
    Encrypt a file using:
    AES-256-CBC
    PBKDF2-HMAC-SHA256
    HMAC-SHA256
    """

    with open(input_path, "rb") as file:
        plaintext = file.read()

    # Generate random salt and IV
    salt = os.urandom(SALT_SIZE)
    iv = os.urandom(IV_SIZE)

    # Derive encryption and MAC keys
    encryption_key, mac_key = derive_keys(password, salt)

    # Encrypt file
    ciphertext = aes_encrypt(
        plaintext,
        encryption_key,
        iv
    )

    # Build data that will be authenticated
    authenticated_data = (
        MAGIC +
        salt +
        iv +
        ciphertext
    )

    # Calculate HMAC
    mac = hmac.new(
        mac_key,
        authenticated_data,
        hashlib.sha256
    ).digest()

    # Final encrypted file format:
    #
    # MAGIC
    # SALT
    # IV
    # CIPHERTEXT
    # HMAC
    #

    with open(output_path, "wb") as file:
        file.write(authenticated_data)
        file.write(mac)


# ============================================================
# FILE DECRYPTION
# ============================================================

def decrypt_file(input_path: str, output_path: str, password: str):
    """
    Decrypt an encrypted file.

    HMAC is verified BEFORE attempting decryption.
    """

    with open(input_path, "rb") as file:
        encrypted_data = file.read()

    minimum_size = (
        len(MAGIC) +
        SALT_SIZE +
        IV_SIZE +
        BLOCK_SIZE +
        MAC_SIZE
    )

    if len(encrypted_data) < minimum_size:
        raise ValueError("Invalid encrypted file.")

    # Read file components
    magic = encrypted_data[:4]

    if magic != MAGIC:
        raise ValueError(
            "Invalid file format. This is not a File Protection Utility encrypted file."
        )

    salt_start = 4
    salt_end = salt_start + SALT_SIZE

    iv_start = salt_end
    iv_end = iv_start + IV_SIZE

    mac_start = len(encrypted_data) - MAC_SIZE

    salt = encrypted_data[salt_start:salt_end]
    iv = encrypted_data[iv_start:iv_end]

    ciphertext = encrypted_data[iv_end:mac_start]

    received_mac = encrypted_data[mac_start:]

    # Derive keys
    encryption_key, mac_key = derive_keys(password, salt)

    # Recreate authenticated data
    authenticated_data = (
        MAGIC +
        salt +
        iv +
        ciphertext
    )

    # Calculate expected MAC
    expected_mac = hmac.new(
        mac_key,
        authenticated_data,
        hashlib.sha256
    ).digest()

    # Secure constant-time comparison
    if not hmac.compare_digest(received_mac, expected_mac):
        raise ValueError(
            "Integrity verification failed. Wrong password or file has been modified."
        )

    # Decrypt only after MAC verification
    plaintext = aes_decrypt(
        ciphertext,
        encryption_key,
        iv
    )

    with open(output_path, "wb") as file:
        file.write(plaintext)