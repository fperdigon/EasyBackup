import json
import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

def generate_key():
    """Generate a 32-byte (256-bit) AES key and return it in base64 format."""
    return base64.urlsafe_b64encode(os.urandom(32)).decode()

def encrypt_json(data, key):
    """
    Encrypts JSON data using AES encryption.
    
    Args:
    - data (dict): JSON data to encrypt.
    - key (str): Base64-encoded AES key.

    Returns:
    - encrypted_data (str): Encrypted JSON as a base64-encoded string.
    - iv (str): Base64-encoded Initialization Vector.
    """
    key = base64.urlsafe_b64decode(key)  # Decode the key from base64
    iv = os.urandom(16)  # Generate a random IV (Initialization Vector)

    # Convert JSON data to a string and pad it
    json_string = json.dumps(data)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(json_string.encode()) + padder.finalize()

    # Encrypt using AES CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_bytes = encryptor.update(padded_data) + encryptor.finalize()

    # Encode the encrypted data and IV in base64 for storage
    encrypted_data = base64.b64encode(encrypted_bytes).decode()
    iv_encoded = base64.b64encode(iv).decode()

    return encrypted_data, iv_encoded

def decrypt_json(encrypted_data, iv, key):
    """
    Decrypts AES-encrypted JSON data.

    Args:
    - encrypted_data (str): Base64-encoded encrypted JSON.
    - iv (str): Base64-encoded Initialization Vector.
    - key (str): Base64-encoded AES key.

    Returns:
    - dict: Decrypted JSON data.
    """
    key = base64.urlsafe_b64decode(key)
    iv = base64.b64decode(iv)
    encrypted_data = base64.b64decode(encrypted_data)

    # Decrypt using AES CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()

    # Unpad the decrypted data
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_data = unpadder.update(decrypted_padded) + unpadder.finalize()

    # Convert back to JSON
    return json.loads(decrypted_data.decode())

def save_encrypted_json(file_path, data, key):
    """Encrypts JSON data and saves it to a file."""
    encrypted_data, iv = encrypt_json(data, key)
    with open(file_path, "w") as f:
        json.dump({"iv": iv, "data": encrypted_data}, f)

def load_encrypted_json(file_path, key):
    """Loads and decrypts JSON data from a file."""
    with open(file_path, "r") as f:
        encrypted_content = json.load(f)
    return decrypt_json(encrypted_content["data"], encrypted_content["iv"], key)

# Example Usage
if __name__ == "__main__":
    key = generate_key()  # Generate a new key (store this securely)
    print("Encryption Key (Save this securely!):", key)

    json_data = {"username": "admin", "password": "securepass"}
    file_path = "encrypted_data.json"

    save_encrypted_json(file_path, json_data, key)
    print("Encrypted JSON saved.")

    decrypted_data = load_encrypted_json(file_path, key)
    print("Decrypted JSON:", decrypted_data)
