import binascii
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

import bcrypt

from kompanion_py.core.config import AuthSettings
from kompanion_py.models import Device, Session, User

from .exceptions import (
    DeviceAlreadyExistsError,
    DeviceNotFoundError,
    InvalidCredentialsError,
    SessionNotFoundError,
    UserAlreadyExistsError,
)
from .repository import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository, auth_settings: AuthSettings):
        self.user_repository = user_repository
        self.auth_settings = auth_settings

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    @staticmethod
    def _hash_koreader_sync_password(password: str) -> str:
        md5_hash = hashlib.md5(password.encode("utf-8")).digest()
        return binascii.hexlify(md5_hash).decode("utf-8")

    def register_user(self, username: str, password: str) -> User:
        if self.user_repository.get_user_by_username(username):
            raise UserAlreadyExistsError(username)

        hashed_password = self.hash_password(password)
        user = User(username=username, hashed_password=hashed_password)
        return self.user_repository.create_user(user)

    def login(
        self,
        username: str,
        password: str,
        user_agent: Optional[str] = None,
        client_ip: Optional[str] = None,
    ) -> Session:
        user = self.user_repository.get_user_by_username(username)
        if not user or not self.verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        session_key = binascii.hexlify(uuid4().bytes).decode("utf-8")
        expires_at = datetime.utcnow() + timedelta(
            seconds=self.auth_settings.jwt_expires_in
        )
        session = Session(
            session_key=session_key,
            user_id=user.id,
            user_agent=user_agent,
            client_ip=client_ip,
            expires_at=expires_at,
        )
        return self.user_repository.store_session(session)

    def logout(self, session_key: str) -> None:
        self.user_repository.delete_session_by_key(session_key)

    def get_user_from_session(self, session_key: str) -> Optional[User]:
        session = self.user_repository.get_session_by_key(session_key)
        if not session or session.expires_at < datetime.utcnow():
            if session: # Delete expired session
                self.user_repository.delete_session_by_key(session_key)
            raise SessionNotFoundError()

        return self.user_repository.get_user_by_id(session.user_id)

    def add_user_device(
        self, user_id: UUID, device_name: str, device_password: str
    ) -> Device:
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            # This case should ideally not be reached if user_id comes from a valid session
            raise InvalidCredentialsError() # Or a more specific UserNotFoundError

        if self.user_repository.get_device_by_name(device_name):
            raise DeviceAlreadyExistsError(device_name)

        hashed_device_password = self._hash_koreader_sync_password(device_password)
        device = Device(
            name=device_name, hashed_password=hashed_device_password, user_id=user_id
        )
        return self.user_repository.create_device(device)

    def deactivate_user_device(self, device_name: str, user_id: UUID) -> None:
        device = self.user_repository.get_device_by_name(device_name)
        if not device:
            raise DeviceNotFoundError(device_name)

        if device.user_id != user_id:
            # Attempting to delete a device not owned by the user
            raise DeviceNotFoundError(device_name) # Or a more specific permission error

        self.user_repository.delete_device_by_name(device_name)

    def verify_device_password(
        self, device_name: str, password: str, is_hash: bool = False
    ) -> bool:
        device = self.user_repository.get_device_by_name(device_name)
        if not device:
            raise DeviceNotFoundError(device_name)

        if is_hash:
            return device.hashed_password == password
        else:
            return device.hashed_password == self._hash_koreader_sync_password(password)

    def list_user_devices(self, user_id: UUID) -> list[Device]:
        return self.user_repository.list_devices_by_user_id(user_id)
