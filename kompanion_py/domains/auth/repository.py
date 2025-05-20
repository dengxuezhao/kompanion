import abc
from typing import Optional
from uuid import UUID

from kompanion_py.models import Device, Session, User

from .exceptions import DeviceAlreadyExistsError, UserAlreadyExistsError


class UserRepository(abc.ABC):
    @abc.abstractmethod
    def create_user(self, user: User) -> User:
        pass

    @abc.abstractmethod
    def get_user_by_username(self, username: str) -> Optional[User]:
        pass

    @abc.abstractmethod
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        pass

    @abc.abstractmethod
    def store_session(self, session: Session) -> Session:
        pass

    @abc.abstractmethod
    def get_session_by_key(self, session_key: str) -> Optional[Session]:
        pass

    @abc.abstractmethod
    def delete_session_by_key(self, session_key: str) -> None:
        pass

    @abc.abstractmethod
    def create_device(self, device: Device) -> Device:
        pass

    @abc.abstractmethod
    def get_device_by_name(self, name: str) -> Optional[Device]:
        pass

    @abc.abstractmethod
    def delete_device_by_name(self, name: str) -> None:
        pass

    @abc.abstractmethod
    def list_devices_by_user_id(self, user_id: UUID) -> list[Device]:
        pass


class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._users: dict[UUID, User] = {}
        self._users_by_username: dict[str, UUID] = {}
        self._sessions: dict[str, Session] = {}
        self._devices: dict[UUID, Device] = {}
        self._devices_by_name: dict[str, UUID] = {}

    def create_user(self, user: User) -> User:
        if user.username in self._users_by_username:
            raise UserAlreadyExistsError(user.username)
        new_user = user.copy(deep=True)
        self._users[new_user.id] = new_user
        self._users_by_username[new_user.username] = new_user.id
        return new_user.copy(deep=True)

    def get_user_by_username(self, username: str) -> Optional[User]:
        user_id = self._users_by_username.get(username)
        if user_id:
            user = self._users.get(user_id)
            return user.copy(deep=True) if user else None
        return None

    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        user = self._users.get(user_id)
        return user.copy(deep=True) if user else None

    def store_session(self, session: Session) -> Session:
        new_session = session.copy(deep=True)
        self._sessions[new_session.session_key] = new_session
        return new_session.copy(deep=True)

    def get_session_by_key(self, session_key: str) -> Optional[Session]:
        session = self._sessions.get(session_key)
        return session.copy(deep=True) if session else None

    def delete_session_by_key(self, session_key: str) -> None:
        if session_key in self._sessions:
            del self._sessions[session_key]

    def create_device(self, device: Device) -> Device:
        if device.name in self._devices_by_name:
            raise DeviceAlreadyExistsError(device.name)
        new_device = device.copy(deep=True)
        self._devices[new_device.id] = new_device
        self._devices_by_name[new_device.name] = new_device.id
        return new_device.copy(deep=True)

    def get_device_by_name(self, name: str) -> Optional[Device]:
        device_id = self._devices_by_name.get(name)
        if device_id:
            device = self._devices.get(device_id)
            return device.copy(deep=True) if device else None
        return None

    def delete_device_by_name(self, name: str) -> None:
        device_id = self._devices_by_name.pop(name, None)
        if device_id and device_id in self._devices:
            del self._devices[device_id]

    def list_devices_by_user_id(self, user_id: UUID) -> list[Device]:
        return [
            dev.copy(deep=True)
            for dev in self._devices.values()
            if dev.user_id == user_id
        ]
