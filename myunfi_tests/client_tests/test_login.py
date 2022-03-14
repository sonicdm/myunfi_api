import os
from unittest import TestCase
from myunfi.client.login import do_login
import requests


class TestMyUNFILogin(TestCase):
    def test_login(self):
        # user and password from environment
        # s = requests.Session()
        s = requests.Session()
        username = os.environ.get('MYUNFI_USERNAME')
        password = os.environ.get('MYUNFI_PASSWORD')
        login = do_login(s, username, password)

        self.assertTrue(login)


