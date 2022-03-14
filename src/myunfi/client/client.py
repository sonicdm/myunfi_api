"""
MyUnfi Client Base Class
"""

from urllib.parse import unquote

import requests
from ..http_wrappers import factories
from bs4 import BeautifulSoup

from myunfi.config import login_page, login_redirect_url, home_page
from myunfi.utils.logging import get_logger
from .base import MyUNFIClientProtocol
from .client_exceptions import MyUnfiInvalidLoginRedirect, MyUnfiInvalidCredentials, MyUnfiLoginFormNotFound
from .headers import login_page_headers
from .login import do_login, is_authorized
wrapper_factory = factories.HTTPWrapperFactory()
LOGGER = get_logger(__name__)


class MyUNFIClient(MyUNFIClientProtocol):
    """
    MyUNFI Client
    Creates a session for use in python projects needing to communicate with MyUNFI
    Usage:
        client = MyUNFIClient(username="", password="")
    """

    def __init__(self, username=None, password=None, auto_login=True, auto_reconnect=True, session=None):
        """

        :param username:
        :param password:
        """
        super().__init__(username, password, auto_login)
        self.session = session or wrapper_factory.get_session().create_session()
        self.logger = LOGGER.getChild(self.__class__.__name__)
        if self.auto_login and username and password:
            self.login(username, password)

    def login(self, username, password) -> None:
        try:
            if do_login(self.session, username, password):
                self.logger.info("Successfully logged in")
                self.logged_in = True
        except MyUnfiInvalidLoginRedirect as e:
            self.logger.error(e)
            self.logged_in = False
            raise
        except MyUnfiInvalidCredentials as e:
            self.logger.error(e)
            self.logged_in = False
            raise
        except MyUnfiLoginFormNotFound as e:
            self.logger.error(e)
            self.logged_in = False
            raise

    def logout(self) -> None:
        if not self.logged_in:
            self.logger.warning("Tried to log out whe not logged in")
            return
        pass

    def get_login_page(self) -> str:
        pass

    def get_logout_page(self) -> str:
        pass

    def is_logged_in(self) -> bool:
        if self.logged_in:
            authorized = is_authorized(self.session)
            if authorized:
                return True
            else:
                self.logger.warning("Session has expired")
                self.logged_in = False
        return self.logged_in

    def get_session(self):
        return self.session

    def check_auth(self):
        pass

    def do_request(self, method, url, **kwargs):
        response = self.session.request(method, url, **kwargs)
        return response


