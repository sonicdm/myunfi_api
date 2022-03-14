#!/usr/bin/env python3
import json

from requests import Response, status_codes
from unfi_api.api.response import APIResponse


def response_to_json(response: Response) -> dict:
    """
    :type response: `requests.models.Response`
    :param response:
    :return:
    """
    error = None
    data = None
    status = None
    if not isinstance(response, Response):
        error = f"response value must be type %r got %r instead" % (Response, response)
    content_type = response.headers.get('content-type')
    status = response.status_code
    if not response.ok:
            data = None
            error = response.reason
                    
    elif ('application/json' in content_type or 'text/json' in content_type or 'text/plain' in content_type):
            try:
                data = response.json()

            except json.JSONDecodeError as exception:
                error = f"Invalid JSON Format {exception}"
                data = ""

    result = {
        "error": error,
        "status": status,
        "data": data,
        "content": response.content,
        "content_type": content_type,
        "url": response.request.url,
        "text": response.text,
        "response": response
    }
    return result


def response_to_api_response(response, api_response: APIResponse=APIResponse) -> APIResponse:
    """
    :type response: `requests.models.Response`
    :param response:
    :return:
    """
    result = response_to_json(response)
    return api_response.parse_obj(result)
