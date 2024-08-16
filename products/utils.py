from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from hashlib import sha256
from base64 import b64encode, b64decode

class AESCipher:
    def __init__(self, key):
        self.block_size = AES.block_size
        self.key = sha256(key.encode()).digest()

    def pad(self, s):
        padding_length = self.block_size - len(s) % self.block_size
        return s + chr(padding_length) * padding_length

    def unpad(self, s):
        return s[:-ord(s[len(s)-1:])]

    def encrypt(self, raw):
        raw = self.pad(raw)
        iv = get_random_bytes(self.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypted_data = iv + cipher.encrypt(raw.encode())
        encrypted_b64 = b64encode(encrypted_data).decode()
        # print(f"Encrypted (Base64): {encrypted_b64}")
        return b64encode(encrypted_data).decode()

    def decrypt(self, enc):
        # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@####################################",enc.encode())
        enc = b64decode(enc.encode())
        # print("##################################################################",enc)
        iv = enc[:self.block_size]
        print("iv", iv)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted_data = self.unpad(cipher.decrypt(enc[self.block_size:])).decode()
        print(f"Decrypted: {decrypted_data}")
        return decrypted_data
