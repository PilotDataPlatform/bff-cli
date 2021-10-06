
class Error(Exception):
    pass

class InvalidEncryptionError(Error):
    def __init__(self, message="Invalid encryption"):
        super().__init__(message)