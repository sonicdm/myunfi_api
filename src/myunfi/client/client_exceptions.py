"""
MyUNFI Client Exceptions
"""


class MyUnfiClientException(Exception):
    pass


class MyUnfiInvalidLoginRedirect(MyUnfiClientException):
    def __init__(self, url, expected_url=None):
        self.url = url
        self.expected_url = expected_url
        super(MyUnfiInvalidLoginRedirect, self).__init__(f"Invalid login redirect: {url} Expected: {expected_url}")

    def __str__(self):
        return f"Invalid login redirect: {self.url} Expected: {self.expected_url}"

    def __repr__(self):
        return f"MyUnfiInvalidLoginRedirect({self.url}, {self.expected_url})"


class MyUnfiInvalidCredentials(MyUnfiClientException):
    pass


class MyUnfiLoginFormNotFound(MyUnfiClientException):
    pass

class MyUnfiFailedAuthorization(MyUnfiClientException):
    pass
