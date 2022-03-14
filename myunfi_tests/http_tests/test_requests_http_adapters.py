import unittest
import json

from myunfi.http_wrappers.http_adapters import HTTPAdapter, HTTPResponse, HTTPSession, HTTPRequest
from myunfi.http_wrappers.http_requests import RequestsSession


class MockResult(object):
    def __init__(self, status_code, name=None, text: str = None, content: bytes = None, headers: dict = None,
                 cookies: dict = None, history: bool = False, *args, **kwargs):
        self.name = name
        self.status_code = status_code
        self.content = content or text.encode('utf-8')
        if text is None:
            self.text = content.decode('utf-8')
        else:
            self.text = text
        self.cookies = cookies or {"session": "1234567890",
                                   "csrf_token": "1234567890",
                                   "path": "/; HttpOnly"
                                   }

        self.headers = headers or {'Content-Type': 'text/plain',
                                   'Content-Length': 12,
                                   "Content-Disposition": "attachment; filename=test.txt",
                                   "Set-Cookie": ", ".join(["=".join(kv) for kv in self.cookies.items()])
                                   }
        self.elapsed = 0.0
        self.request = None
        if history:
            self.history = [
                MockResult(302, text="Redirect1", headers={"Content-Type": "text/plain"}),
                MockResult(302, text="Redirect2", headers={"Content-Type": "text/plain"}),
            ]

        self.encoding = 'utf-8'
        self.args = args
        self.kwargs = kwargs

    def json(self):
        return json.loads(self.text)

    def __str__(self):
        if self.name is not None:
            return self.name
        return self.text


class MockSession:

    def __init__(self):
        self.text = None
        self.status_code = None
        self.cookies = {"session": "1234567890"}
        self.headers = {
            'session_id': '1234567890',
            'session_expiry': '1234567890',
            'connection': 'keep-alive',
            'date': 'Mon, 01 Jan 2000 00:00:00 GMT',
        }

    def mock_method(self, method, verb, url, headers=None, cookies=None, *args, **kwargs):
        headers = headers or self.headers
        cookies = cookies or self.cookies
        text = self.text
        default_text = f'{method=} {verb=} {url=} {headers=} {cookies=} {args=} {kwargs=}'
        if not text:
            text = default_text
        content = text.encode("utf-8") or kwargs.get('data') or b''
        return MockResult(self.status_code, content=content, name=default_text, cookies=cookies, headers=headers, *args, **kwargs)

    def request(self, method, url, *args, **kwargs):
        return self.mock_method("request", method, url, *args, **kwargs)

    def get(self, url, headers=None, cookies=None, *args, **kwargs):
        return self.mock_method("get", "GET", url, headers, cookies, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        return self.mock_method("post", "POST", url, *args, **kwargs)

    def put(self, url, *args, **kwargs):
        return self.mock_method("put", "PUT", url, *args, **kwargs)

    def patch(self, url, *args, **kwargs):
        return self.mock_method("patch", "PATCH", url, *args, **kwargs)

    def head(self, url, *args, **kwargs):
        return self.mock_method("head", "HEAD", url, *args, **kwargs)

    def delete(self, url, *args, **kwargs):
        return self.mock_method("delete", "DELETE", url, *args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class TestRequestsSession(unittest.TestCase):
    pass

    def test_session_init(self):
        headers = {
            'session_id': '1234567890',
            'session_expiry': '1234567890',
            'connection': 'keep-alive',
            'date': 'Mon, 01 Jan 2000 00:00:00 GMT',
        }

        cookies = {"session": "1234567890"}
        mock_requests_session = MockSession()
        mock_requests_session.headers = headers
        mock_requests_session.cookies = cookies
        mock_requests_session.status_code = 200
        session = RequestsSession(mock_requests_session)
        self.assertEqual(session.headers, headers)
        self.assertEqual(session.cookies, cookies)

        self.assertEqual(mock_requests_session, session.get_session())

        pass

    def test_session_get(self):
        mock_requests_session = MockSession()
        mock_requests_session.status_code = 200
        mock_requests_session.text = '{"status": "ok"}'
        session = RequestsSession(mock_requests_session)
        response = session.get('/')
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '{"status": "ok"}')
        self.assertEqual(response.cookies, mock_requests_session.cookies)

    def test_session_request(self):
        mock_requests_session = MockSession()
        mock_requests_session.status_code = 200
        mock_requests_session.text = '{"status": "ok"}'
        session = RequestsSession(mock_requests_session)
        response = session.request('GET', '/')
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '{"status": "ok"}')
        self.assertEqual(response.cookies, mock_requests_session.cookies)
        self.assertEqual(response.headers, mock_requests_session.headers)

    def test_session_post(self):
        mock_requests_session = MockSession()
        mock_requests_session.status_code = 200
        mock_requests_session.text = '{"status": "ok"}'
        session = RequestsSession(mock_requests_session)
        response = session.post('/')
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '{"status": "ok"}')
        self.assertEqual(response.cookies, mock_requests_session.cookies)
        self.assertEqual(response.headers, mock_requests_session.headers)


    def test_session_put(self):
        mock_requests_session = MockSession()
        mock_requests_session.status_code = 200
        mock_requests_session.text = '{"status": "ok"}'
        session = RequestsSession(mock_requests_session)
        response = session.put('/')
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '{"status": "ok"}')
        self.assertEqual(response.cookies, mock_requests_session.cookies)
        self.assertEqual(response.headers, mock_requests_session.headers)

    def test_session_patch(self):
        mock_requests_session = MockSession()
        mock_requests_session.status_code = 200
        mock_requests_session.text = '{"status": "ok"}'
        session = RequestsSession(mock_requests_session)
        response = session.patch('/')
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '{"status": "ok"}')
        self.assertEqual(response.cookies, mock_requests_session.cookies)
        self.assertEqual(response.headers, mock_requests_session.headers)

    def test_session_delete(self):
        mock_requests_session = MockSession()
        mock_requests_session.status_code = 200
        mock_requests_session.text = '{"status": "ok"}'
        session = RequestsSession(mock_requests_session)
        response = session.delete('/')
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '{"status": "ok"}')
        self.assertEqual(response.cookies, mock_requests_session.cookies)
        self.assertEqual(response.headers, mock_requests_session.headers)

    def test_session_head(self):
        mock_requests_session = MockSession()
        mock_requests_session.status_code = 200
        mock_requests_session.text = '{"status": "ok"}'
        session = RequestsSession(mock_requests_session)
        response = session.head('/')
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '{"status": "ok"}')
        self.assertEqual(response.cookies, mock_requests_session.cookies)
        self.assertEqual(response.headers, mock_requests_session.headers)
