
class Error(Exception):
    pass

class InvalidEncryptionError(Error):
    def __init__(self, message="Invalid encryption"):
        super().__init__(message)

class HPCError(Error):
    def __init__(self, code, message="HPC error"):
        self.code = code
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"