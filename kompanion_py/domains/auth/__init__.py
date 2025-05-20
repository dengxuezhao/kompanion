# Auth domain module

from .exceptions import (
    DeviceNotFoundError,
    InvalidCredentialsError,
    DeviceAlreadyExistsError,
    SessionNotFoundError,
    InvalidCredentialsError,
    SessionNotFoundError,
    UserAlreadyExistsError,
)
from .repository import InMemoryUserRepository, UserRepository
from .service import AuthService  # Forward declaration

__all__ = [
    "AuthService",
    "UserRepository",
    "InMemoryUserRepository",
    "UserAlreadyExistsError",
    "InvalidCredentialsError",
    "SessionNotFoundError",
    "DeviceNotFoundError",
    "DeviceAlreadyExistsError",
]
