class AuthError(Exception):
    """Base class for authentication errors."""

    pass


class UserAlreadyExistsError(AuthError):
    """Raised when trying to register a user that already exists."""

    def __init__(self, username: str):
        self.username = username
        super().__init__(f"User '{username}' already exists.")


class InvalidCredentialsError(AuthError):
    """Raised when login credentials are invalid."""

    def __init__(self):
        super().__init__("Invalid username or password.")


class SessionNotFoundError(AuthError):
    """Raised when a session is not found or is invalid."""

    def __init__(self):
        super().__init__("Session not found or invalid.")


class DeviceNotFoundError(AuthError):
    """Raised when a device is not found."""

    def __init__(self, device_name: Optional[str] = None):
        self.device_name = device_name
        if device_name:
            super().__init__(f"Device '{device_name}' not found.")
        else:
            super().__init__("Device not found.")


class DeviceAlreadyExistsError(AuthError):
    """Raised when trying to add a device that already exists."""

    def __init__(self, device_name: str):
        self.device_name = device_name
        super().__init__(f"Device '{device_name}' already exists.")
