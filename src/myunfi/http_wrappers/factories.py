from typing import Type

from myunfi.config import http_library
from myunfi.http_wrappers.http_requests import HTTPRequestsRequest, RequestsResult, RequestsSession
from myunfi.http_wrappers.http_adapters import HTTPResult, HTTPRequest, HTTPSession

Session = HTTPSession
Request = HTTPRequest
Result = HTTPResult

if http_library == "requests":
    import requests

    Result = RequestsResult
    Request = HTTPRequestsRequest
    Session = RequestsSession


def get_session() -> Type[HTTPSession]:
    return Session


def get_request() -> Type[HTTPRequest]:
    return Request


def get_result() -> Type[HTTPResult]:
    return Result


class HTTPWrapperFactory:
    def __init__(self):
        self.session = get_session()
        self.request = get_request()
        self.result = get_result()

    def get_session(self) -> Type[HTTPSession]:
        return self.session

    def get_request(self) -> Type[HTTPRequest]:
        return self.request

    def get_result(self) -> Type[HTTPResult]:
        return self.result
