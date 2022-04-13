class MirCtrError(Exception):
    """
    error raised by ymir-controller
    """
    def __init__(self, error_code: int, error_message: str) -> None:
        super().__init__()
        self.error_code = error_code
        self.error_message = error_message

    def __str__(self) -> str:
        return f"code: {self.error_code}, content: {self.error_message}"
