from __future__ import annotations
import abc
import json
from typing import TYPE_CHECKING
from .exceptions import *
import os
from pathlib import Path
import re


if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Union
    from myunfi.http_wrappers.http_adapters import HTTPResult


class HTTPResponse(abc.ABC):
    def __init__(self, response: HTTPResult):
        self.status_code = response.get_status_code()
        self.content = response.get_content()
        self.text = response.get_text()
        self.headers = response.get_headers()
        self.cookies = response.get_cookies()
        self.content_type = response.get_content_type()
        self.url = response.get_url()

    def get_status_code(self):
        return self.status_code

    def get_content(self):
        return self.content

    def get_headers(self):
        return self.headers

    def get_json(self):
        return json.loads(self.get_text())

    def get_text(self):
        return self.text

    def get_cookies(self):
        return self.cookies

    def get_content_type(self):
        return self.content_type

    def get_url(self):
        return self.url


class DataResponse(HTTPResponse):
    def __init__(self, response: HTTPResult):
        super().__init__(response)
        self.data = self.get_content()
        if not self.data:
            raise EmptyResponseException()

    def get_data(self):
        return self.data

    def get_filename(self):
        """
        Get filename from content-disposition header if not found, return last part of url without query string
        :return:
        """
        content_disposition = self.get_headers().get('Content-Disposition', '')
        if content_disposition:
            return content_disposition.split('filename=')[1]
        else:
            basename = os.path.basename(self.get_url())
            return re.split('[?#]', basename)[0]

    def save_to_file(self, path: str):
        path = Path(path)
        if path.is_dir():
            path = path / self.get_filename()
        with path.open('wb') as f:
            path.parent.mkdir(parents=True, exist_ok=True)
            f.write(self.get_data())
            f.close()

    def append_to_file(self, path: str):
        path = Path(path)
        if path.is_dir():
            path = path / self.get_filename()
        with path.open('ab') as f:
            path.parent.mkdir(parents=True, exist_ok=True)
            f.write(self.get_data())
            f.close()


class JSONResponse(HTTPResponse):
    def __init__(self, response: HTTPResult):
        super().__init__(response)
        try:
            self.json = self.get_json()
        except json.JSONDecodeError:
            self.json = None
            raise NonJSONResponseException("Response is not JSON")


class TextResponse(HTTPResponse):
    def __init__(self, response: HTTPResult):
        super().__init__(response)
        # ensure that the response is text
        if not self.get_content_type().startswith("text"):
            raise NonTextResponseException("Response is not text")
        self.text = self.get_text()


class ImageResponse(DataResponse):
    def __init__(self, response: HTTPResult):
        super().__init__(response)
        # ensure that the response is any image type
        if not self.get_content_type().startswith("image/"):
            raise NonImageResponseException("Response is not an image")
        self.image = self.get_content()


class HTMLResponse(HTTPResponse):
    def __init__(self, response: HTTPResult):
        super().__init__(response)
        # ensure that the response is any image type
        if self.get_content_type() not in ["text/html"]:
            raise NonHTMLResponseException(f"Expected HTML, got {self.get_content_type()}")
        self.html = self.get_text()


class PDFResponse(DataResponse):
    def __init__(self, response: HTTPResult):
        super().__init__(response)
        # ensure that the response is any image type
        if self.get_content_type() not in ["application/pdf"]:
            raise NonPDFResponseException(f"Expcted PDF response, got {self.get_content_type()}")
        self.pdf = self.get_content()


class ExcelResponse(DataResponse):
    EXCEL_TYPES = ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]

    def __init__(self, response: HTTPResult):
        super().__init__(response)
        # ensure that the response is any image type
        if self.get_content_type() not in self.EXCEL_TYPES:
            raise NonExcelResponseException(f"Expected one of {self.EXCEL_TYPES}, got {self.get_content_type()}")
        self.excel = self.get_content()


class CSVResponse(DataResponse):
    def __init__(self, response: HTTPResult):
        super().__init__(response)
        # ensure that the response is any image type
        if self.get_content_type() not in ["text/csv"]:
            raise NonCSVResponseException(f"Expected text/csv, got {self.get_content_type()}")


class XMLResponse(DataResponse):
    def __init__(self, response: HTTPResult):
        super().__init__(response)
        # ensure that the response is any image type
        if self.get_content_type() not in ["text/xml"]:
            raise NonXMLResponseException(f"Expected text/xml, got {self.get_content_type()}")
        self.xml = self.get_text()


class BytesResponse(DataResponse):
    def __init__(self, response: HTTPResult):
        super().__init__(response)
        # ensure that the response is any image type
        if self.get_content_type() not in ["application/octet-stream"]:
            raise NonBytesResponseException(f"Expected application/octet-stream, got {self.get_content_type()}")
        self.bytes = self.get_content()


class VideoResponse(DataResponse):
    def __init__(self, response: HTTPResult):
        super().__init__(response)
        # ensure that the response is any image type
        if not self.get_content_type().startswith("video/"):
            raise NonVideoResponseException(f"Expected video, got {self.get_content_type()}")
        self.video = self.get_content()
