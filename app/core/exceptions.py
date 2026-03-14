class AppException(Exception):
    def __init__(self, error_code: int, error_desc: str, status_code: int = 400):
        self.error_code = error_code
        self.error_desc = error_desc
        self.status_code = status_code
