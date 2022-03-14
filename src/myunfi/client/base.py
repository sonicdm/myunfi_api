"""
MyUNFI Client Baseclass
"""
from abc import ABC, abstractmethod


class MyUNFIClientProtocol(ABC):
    def __init__(self, username: str, password: str, auto_login: bool = True) -> None:
        self.username = username
        self.password = password
        self.auto_login = auto_login
        self.logged_in = False
        self.session = None

    @abstractmethod
    def login(self, username, password) -> None:
        pass

    @abstractmethod
    def logout(self) -> None:
        pass

    @abstractmethod
    def get_login_page(self) -> str:
        pass

    @abstractmethod
    def get_logout_page(self) -> str:
        pass

    def is_logged_in(self) -> bool:
        return self.logged_in

    def __repr__(self):
        return f"<{self.__class__.__name__} username={self.username} logged_in={self.logged_in}>"
