from __future__ import annotations

from myunfi.http_wrappers.http_adapters import HTTPResult


class URLLibResponse(HTTPResult):
    """
    TODO: Implement
    Adapter for urllib.request.urlopen
    """

    def get_content_type(self):
        pass

    def get_content(self):
        pass

    def get_headers(self):
        pass

    def get_json(self):
        pass

    def get_cookies(self):
        pass

    def get_status_code(self):
        pass

    def get_text(self):
        pass

    def get_url(self):
        pass