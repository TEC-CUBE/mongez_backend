from cryptography.fernet import Fernet


def encrypt_message(message, key):
    """
    Encrypts a message
    """
    encoded_message = message.encode()
    f = Fernet(key)
    return f.encrypt(encoded_message)


def decrypt_message(encrypted_message, key):
    """
    Decrypts an encrypted message
    """
    f = Fernet(key)
    return f.decrypt(encrypted_message)
