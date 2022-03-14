from __future__ import annotations
from typing import Type

import requests
from requests import Session
from requests.cookies import RequestsCookieJar
from requests.structures import CaseInsensitiveDict

from myunfi.http_wrappers.http_adapters import HTTPRequest, HTTPResult, HTTPSession


class HTTPRequestsRequest(HTTPRequest):
    def __init__(self, verb, url, headers=None, params=None, json=None, data=None, cookies=None,
                 session: RequestsSession = None, append_to_session=False):
        super().__init__(verb, url, headers, params, json, data, cookies, session, append_to_session)
        if not self.requester:
            self.requester = RequestsSession(requests.Session())
            if self.headers:
                if self.append_to_session:
                    self.requester.headers = self.requester.headers.update(self.headers)
                    self.headers = self.requester.headers
                else:
                    self.requester.headers = self.headers

            if self.cookies:
                if self.append_to_session:
                    self.requester.cookies = self.requester.cookies.update(self.cookies)
                    self.cookies = self.requester.cookies
                else:
                    self.requester.cookies = self.cookies


class RequestsSession(HTTPSession):

    def __init__(self, session: Session):
        super().__init__(session)

    def create_request(self, verb: str, url: str, headers: dict = None, params: dict = None,
                       json: dict = None, data: bytes = None,
                       cookies: dict = None, append_to_session: bool = False) -> HTTPRequestsRequest:
        return HTTPRequestsRequest(verb=verb, url=url, headers=headers, params=params, json=json, data=data,
                                   cookies=cookies, session=self, append_to_session=append_to_session)

    def get_session(self):
        if self.session is None:
            self.session = Session()
        return self.session

    @classmethod
    def create_session(cls) -> RequestsSession:
        return RequestsSession(Session())

    def get(self, url, **kwargs) -> RequestsResult:
        return self.request('GET', url, **kwargs)

    def post(self, url, **kwargs) -> RequestsResult:
        return self.request('POST', url, **kwargs)

    def put(self, url, **kwargs) -> RequestsResult:
        return self.request('PUT', url, **kwargs)

    def delete(self, url, **kwargs) -> RequestsResult:
        return self.request('DELETE', url, **kwargs)

    def head(self, url, **kwargs) -> RequestsResult:
        return self.request('HEAD', url, **kwargs)

    def options(self, url, **kwargs) -> RequestsResult:
        return self.request('OPTIONS', url, **kwargs)

    def patch(self, url, **kwargs) -> RequestsResult:
        return self.request('PATCH', url, **kwargs)

    def request(self, method, url, **kwargs) -> RequestsResult:
        res = self.session.request(method, url, **kwargs)
        res.raise_for_status()
        return RequestsResult(res)

    @property
    def headers(self) -> CaseInsensitiveDict[str]:
        return self.session.headers

    @headers.setter
    def headers(self, value):
        self.session.headers = value

    @property
    def cookies(self) -> RequestsCookieJar:
        return self.session.cookies

    @cookies.setter
    def cookies(self, value):
        self.session.cookies = value

    def close(self):
        self.session.close()

    def __enter__(self):
        return self.session.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.__exit__(exc_type, exc_val, exc_tb)


class RequestsResult(HTTPResult):
    """
    Adapter for requests.Response
    """

    def get_status_code(self) -> int:
        return self.response.status_code

    def get_content(self) -> bytes:
        return self.response.content

    def get_headers(self) -> dict:
        return self.response.headers

    def get_json(self) -> dict:
        return self.response.json

    def get_cookies(self) -> dict:
        return self.response.cookies

    def get_text(self) -> str:
        return self.response.text

    def get_url(self) -> str:
        return self.response.url

    def get_content_type(self):
        return self.response.headers.get('content-type')
