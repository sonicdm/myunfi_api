from typing import Type

from bs4 import BeautifulSoup

from myunfi.client.client_exceptions import MyUnfiInvalidCredentials, MyUnfiInvalidLoginRedirect, \
    MyUnfiLoginFormNotFound
from myunfi.client.headers import login_page_headers
from myunfi.config import home_page, login_page, login_redirect_url

from myunfi.http_wrappers import factories
from myunfi.http_wrappers.http_adapters import HTTPResult, HTTPSession
from myunfi.http_wrappers.http_requests import RequestsResult, RequestsSession

fac = factories.HTTPWrapperFactory()


def do_login(session: Type[HTTPSession], username: str, password: str) -> bool:
    """
    Login to the MyUNFI portal
    Returns true or false depending on if the login was successful
    Session will contain a logged in session if successful.
    username: str
    password: str
    """
    session.headers.update(login_page_headers)
    # Get Home Page for session data perhaps
    home_response = session.request("GET", home_page)
    # Get Login Page through the redirect URL. This is the only way to get the session tokens for login.
    login_page_response = session.request("GET", login_redirect_url)

    # make sure the redirect brought us to the right page, this is in config to make it easy to change if required.
    response_base_url = login_page_response.url.split("?")[0]
    if response_base_url != login_page:
        raise MyUnfiInvalidLoginRedirect(response_base_url, login_redirect_url)

    # get login form hidden fields
    login_page_soup = BeautifulSoup(login_page_response.text, "html.parser")
    login_form_hidden_fields = login_page_soup.find("form").find_all("input", type="hidden")
    if not login_form_hidden_fields:
        raise MyUnfiLoginFormNotFound(f"Login form not found on {login_page_response.url}")
    payload = {
        field.get("name"): field.get("value") for field in login_form_hidden_fields
    }
    # add username and password
    payload["USER"] = username
    payload["password"] = password

    # submit login form
    headers = session.headers.copy()
    headers["Referer"] = login_page_response.url
    headers['origin'] = "https://auth.myunfi.com"
    login_response = session.request("post", login_page_response.url, data=payload, headers=headers)
    # check if it is a bad login
    if "Bad Login" in login_response.text or login_response.url == login_page_response.url:
        raise MyUnfiInvalidCredentials("Invalid Username or Password")
    logged_in = is_authorized(session)
    session.headers.update({"x-unfi-host-system": "WBS", "x-unfi-language": "en-US"})
    return logged_in


def is_authorized(session: Type[HTTPSession]) -> bool:
    """
    Checks if the session is authorized
    Returns true or false depending on if the session is authorized
    """
    authorized = session.post("https://www.myunfi.com/api/auth/validate")
    return authorized.status_code == 200
