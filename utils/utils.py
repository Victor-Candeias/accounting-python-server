import os  # For interacting with environment variables
import re  # For regular expressions, used for password complexity rules
import logging  # For logging messages and errors
import base64  # For encoding data
import hashlib  # For creating cryptographic hash values
from bcrypt import checkpw, gensalt, hashpw
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes  # For AES encryption/decryption
from cryptography.hazmat.backends import default_backend  # For selecting the default cryptographic backend
import jwt  # For creating and verifying JSON Web Tokens (JWTs)
from dotenv import load_dotenv  # For loading environment variables from a .env file
from bson import ObjectId  # For handling MongoDB ObjectId
from utils.logging import logging  # Custom logging module

# Load environment variables from the .env file
load_dotenv()

class Utils:
    """
    A utility class that handles various tasks such as encryption, token creation, 
    and password validation.
    """

    def __init__(self):
        """
        Initializes the Utils class by loading encryption settings and password complexity rules.
        - ENCRYPTION_KEY: 32-byte encryption key derived from an environment variable.
        - IV_LENGTH: Length of the initialization vector (IV) for AES encryption.
        """
        self.ENCRYPTION_KEY = hashlib.sha256(os.getenv("ENCRYPTION_KEY").encode()).digest()[:32]  # Generate a 32-byte encryption key
        self.IV_LENGTH = 16  # AES uses a 16-byte IV

    def create_token(self, user):
        """
        Creates a JSON Web Token (JWT) for the given user.
        
        Args:
            user (dict): A dictionary containing user data (e.g., ID and username).
        
        Returns:
            str: The signed JWT token.
        """
        payload = {
            'id': user[0]['_id'],  # MongoDB user ID
            'username': user[0]['username']  # Username
        }
        secret_key = os.getenv("ENCRYPTION_KEY")  # Retrieve the secret key from environment variables
        token = jwt.encode(payload, secret_key, algorithm="HS256")  # Sign the JWT using HMAC and SHA-256
        return token

    def verify_token(self, token):
        """
        Verifies the provided JWT token and returns the decoded payload.
        
        Args:
            token (str): The JWT token to verify.
        
        Returns:
            dict: Decoded token payload if valid, None otherwise.
        """
        if not token:
            logging.error("verify_token();Token required")  # Log if no token is provided
            return None

        try:
            secret_key = os.getenv("ENCRYPTION_KEY")  # Retrieve the secret key from environment variables
            userToken = jwt.decode(token, secret_key, algorithms=['HS256'])  # Decode and verify the token
            return userToken
        except jwt.ExpiredSignatureError as e:
            logging.error(f"verify_token();Token has expired={e}")  # Log if the token has expired
            return None
        except jwt.InvalidTokenError as e:
            logging.error(f"verify_token();Invalid token={e}")  # Log if the token is invalid
            return None

    def encrypt(self, text):
        """
        Encrypts the provided text using AES encryption in CBC mode.
        
        Args:
            text (str): The text to be encrypted.
        
        Returns:
            str: The encrypted text, represented as a hexadecimal string with IV.
        """
        iv = os.urandom(self.IV_LENGTH)  # Generate a random IV
        cipher = Cipher(algorithms.AES(self.ENCRYPTION_KEY), modes.CBC(iv), backend=default_backend())  # AES-CBC cipher
        encryptor = cipher.encryptor()

        # Pad the text to be a multiple of the block size (16 bytes for AES)
        padded_text = text + (algorithms.AES.block_size - len(text) % algorithms.AES.block_size) * chr(algorithms.AES.block_size - len(text) % algorithms.AES.block_size)
        
        # Perform the encryption
        encrypted = encryptor.update(padded_text.encode('utf-8')) + encryptor.finalize()
        
        # Return the IV and encrypted text, both as hex strings
        return iv.hex() + ":" + encrypted.hex()

    def decrypt(self, text):
        """
        Decrypts the provided encrypted text using AES decryption in CBC mode.
        
        Args:
            text (str): The encrypted text, formatted as a hexadecimal string with IV.
        
        Returns:
            str: The decrypted plaintext.
        """
        if not text:
            return ""

        # Split the text to extract IV and encrypted text
        text_parts = text.split(":")
        iv = bytes.fromhex(text_parts[0])  # Convert the IV from hex to bytes
        encrypted_text = bytes.fromhex(text_parts[1])  # Convert the encrypted text from hex to bytes
        
        # Set up the AES-CBC cipher for decryption
        cipher = Cipher(algorithms.AES(self.ENCRYPTION_KEY), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        # Perform the decryption
        decrypted = decryptor.update(encrypted_text) + decryptor.finalize()
        
        # Remove padding
        padding_length = decrypted[-1]
        return decrypted[:-padding_length].decode('utf-8')

    def hash_password(self, password):
        return hashpw(password.encode(), gensalt()).decode()

    def validate_password(self, stored_hash, entered_password):
        return checkpw(entered_password.encode(), stored_hash.encode())

    def validatePassword(self, encryptPassword, sendPassword):
        """
        Validates the provided password by comparing it with its encrypted version.
        
        Args:
            encryptPassword (str): The encrypted password.
            sendPassword (str): The plaintext password to validate.
        
        Returns:
            bool: True if the passwords match, False otherwise.
        """
        decryptPass = self.decrypt(encryptPassword)  # Decrypt the encrypted password
        return decryptPass == sendPassword  # Compare decrypted password with the provided plaintext password
