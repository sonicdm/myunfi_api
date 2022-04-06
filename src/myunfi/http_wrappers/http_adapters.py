from __future__ import annotations
import abc
import mimetypes
from typing import Type
from myunfi.config import random_delay
from myunfi.logger import get_logger
import time, random

from myunfi.http_wrappers.responses import BytesResponse, CSVResponse, ErrorResponse, ExcelResponse, HTMLResponse, \
    ImageResponse, \
    JSONResponse, PDFResponse, TextResponse, HTTPResponse, VideoResponse, XMLResponse

ALLOWED_VERBS = ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"]

logger = get_logger(__name__)


def request_sleep(start: float = 1, stop: float = 3):
    sleep_logger = logger.getChild("request_sleep")
    if random_delay:
        duration = random.uniform(start, stop)
        sleep_logger.debug("Sleeping for %s seconds", duration)
        time.sleep(duration)
        sleep_logger.debug("Done sleeping")


class HTTPAdapter(abc.ABC):
    """
    Abstract base class defining the base interface for HTTP adapters.
    - GET
    - POST
    - PUT
    - DELETE
    - HEAD
    - OPTIONS
    - PATCH
    """

    @abc.abstractmethod
    def get(self, url, **kwargs) -> Type[HTTPResult]:
        pass

    @abc.abstractmethod
    def post(self, url, **kwargs) -> Type[HTTPResult]:
        pass

    @abc.abstractmethod
    def put(self, url, **kwargs) -> Type[HTTPResult]:
        pass

    @abc.abstractmethod
    def delete(self, url, **kwargs) -> Type[HTTPResult]:
        pass

    @abc.abstractmethod
    def head(self, url, **kwargs) -> Type[HTTPResult]:
        pass

    @abc.abstractmethod
    def options(self, url, **kwargs) -> Type[HTTPResult]:
        pass

    @abc.abstractmethod
    def patch(self, url, **kwargs) -> Type[HTTPResult]:
        pass

    @abc.abstractmethod
    def request(self, method, url, sleep=True, **kwargs) -> Type[HTTPResult]:
        pass

    @abc.abstractmethod
    def close(self):
        pass


class HTTPSession(HTTPAdapter):
    def __init__(self, session):
        self.session = session

    def get_session(self) -> Type[HTTPSession]:
        return self.session

    def set_session(self, session):
        self.session = session

    @classmethod
    @abc.abstractmethod
    def create_session(cls) -> Type[HTTPSession]:
        pass

    @property
    @abc.abstractmethod
    def headers(self) -> dict:
        pass

    @headers.setter
    @abc.abstractmethod
    def headers(self, value: dict) -> None:
        pass

    @property
    @abc.abstractmethod
    def cookies(self) -> dict:
        pass

    @cookies.setter
    @abc.abstractmethod
    def cookies(self, value) -> None:
        pass

    @abc.abstractmethod
    def create_request(self, verb: str, url: str, headers: dict = None, params: dict = None, json: dict = None,
                       data: bytes = None, cookies: dict = None, append_to_session: bool = False, **kwargs) -> HTTPRequest:
        pass

    @abc.abstractmethod
    def __enter__(self) -> Type[HTTPSession]:
        pass

    @abc.abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass


class HTTPRequest(abc.ABC):
    def __init__(self, verb, url, headers=None, params=None, json=None, data=None, cookies=None,
                 session: Type[HTTPSession] = None, append_to_session=False):
        """
        Abstraction layer for HTTP requests
        :param verb: HTTP verb
        :param url: URL
        :param headers: HTTP headers
        :param params: HTTP params
        :param data: HTTP data
        :param json: HTTP json
        :param cookies: HTTP cookies
        :param session: OPTIONAL: HTTP session. creates a new session if not provided.
        :param append_to_session: OPTIONAL: Append to existing session info or overwrite headers and cookies
        """
        self.url = url
        self.verb = verb
        self.headers = headers
        self.params = params
        self.data = data
        self.json = json
        self.cookies = cookies
        self.session = session
        self.append_to_session = append_to_session
        self.requester: HTTPSession = None
        self.executed = False
        self.status_code = None
        if session is not None:
            self.requester = session
            if self.headers is not None:
                self.session.headers = self.headers
            if self.cookies is not None:
                self.session.cookies = self.cookies

        self.__response: HTTPResult = None
        self.response_content_type: str = None

    def execute(self) -> Type[HTTPResult]:
        if self.verb.upper() not in ALLOWED_VERBS:
            raise ValueError(f"Invalid verb: {self.verb}")
        self.__response = None
        response = self.requester.request(self.verb, self.url, headers=self.headers, params=self.params, json=self.json,
                                          data=self.data, cookies=self.cookies)

        if response.headers.get('Content-Type') is not None:
            self.response_content_type = response.headers.get('Content-Type').split(';')[0]
        else:
            self.response_content_type = mimetypes.guess_type(response.text)[0]
        self.__response = response
        self.status_code = response.status_code
        self.executed = True
        return self.__response

    def get_json(self) -> JSONResponse:
        return JSONResponse(self.__response)

    def get_text(self) -> TextResponse:
        return TextResponse(self.__response)

    def get_xml(self) -> XMLResponse:
        return XMLResponse(self.__response)

    def get_html(self) -> HTMLResponse:
        return HTMLResponse(self.__response)

    def get_image(self) -> ImageResponse:
        return ImageResponse(self.__response)

    def get_bytes(self) -> BytesResponse:
        return BytesResponse(self.__response)

    def get_csv(self) -> CSVResponse:
        return CSVResponse(self.__response)

    def get_excel(self) -> ExcelResponse:
        return ExcelResponse(self.__response)

    def get_video(self) -> VideoResponse:
        return VideoResponse(self.__response)

    def get_response(self) -> HTTPResponse:
        return HTTPResponse(self.__response)

    def get_pdf(self) -> PDFResponse:
        return PDFResponse(self.__response)

    def get_error(self) -> ErrorResponse:
        return ErrorResponse(self.__response)

    def __repr__(self):
        return f"<HTTPRequest: {self.verb} {self.url} executed={self.executed} status_code={self.status_code}>"


class HTTPResult(abc.ABC):
    def __init__(self, response):
        self.response = response

    @property
    def url(self) -> str:
        return self.get_url()

    @property
    def status_code(self) -> int:
        return self.get_status_code()

    @property
    def headers(self) -> dict:
        return self.get_headers()

    @property
    def cookies(self) -> dict:
        return self.get_cookies()

    @property
    def content(self) -> str:
        return self.get_content()

    @property
    def json(self) -> dict:
        return self.get_json()

    @property
    def text(self) -> str:
        return self.get_text()

    @abc.abstractmethod
    def get_status_code(self) -> int:
        pass

    @abc.abstractmethod
    def get_content(self) -> bytes:
        pass

    @abc.abstractmethod
    def get_headers(self) -> dict:
        pass

    @abc.abstractmethod
    def get_json(self) -> dict:
        pass

    @abc.abstractmethod
    def get_cookies(self) -> dict:
        pass

    @abc.abstractmethod
    def get_text(self) -> str:
        pass

    @abc.abstractmethod
    def get_url(self) -> str:
        pass

    @abc.abstractmethod
    def get_content_type(self) -> str:
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} status_code={self.status_code}, url={self.url}>"
