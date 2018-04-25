from cryptography.fernet import Fernet


class FernetEncryption(object):

    def __init__(self, key):
        self.fernetObject = Fernet(key)

    def encrypt(self, raw):
        return self.fernetObject.encrypt(str.encode(raw))

    def decrypt(self, enc):
        return self.fernetObject.decrypt(str.encode(enc)).decode()
