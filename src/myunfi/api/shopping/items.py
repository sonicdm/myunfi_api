from __future__ import annotations

from typing import Type

from myunfi.http_wrappers.http_adapters import HTTPRequest, HTTPSession
from ...http_wrappers.responses import JSONResponse
import myunfi.logger as logger

"""
shopping_customers_items_endpoints: dict[str,str] = {
    "items": shopping_customers_account_id_items,
    "quantity_on_hand": shopping_customers_account_id_items_quantity_on_hand,
    "recommended": shopping_customers_account_id_items_recommended,
    "search": shopping_customers_account_id_items_search,
    "top": shopping_customers_account_id_items_top,
    "pricing": shopping_customers_account_id_pricing
}
"""
from ..endpoints import shopping_customers_items_endpoints, shopping_customers_categories_endpoints
from myunfi.http_wrappers.factories import get_request as Request


def fetch_product(session: HTTPSession, product_code: str, account_id: str,
                  qty_on_hand_supported: bool = True) -> JSONResponse:
    """
    Fetch a product from the shopping API.
    https://www.myunfi.com/shopping/api/customers/001014/items/61003?isQtyOnHandSupported=true&hostSystem=WBS
    x-unfi-host-system: WBS
    x-unfi-language: en-US
    """
    headers = {
        "x-unfi-host-system": "WBS",
        "x-unfi-language": "en-US",
    }
    session.headers.update(headers)
    endpoint = f'{shopping_customers_items_endpoints["items"]}/{product_code}'
    endpoint = endpoint.format(accountID=account_id) + f"?isQtyOnHandSupported={str(qty_on_hand_supported).lower()}"
    request = session.create_request('get', endpoint, headers=headers)
    request.execute()
    if request.status_code != 200:
        return None
    return request.get_json()
    # result = session.get(endpoint)


def fetch_qty_on_hand(session, account_id: str, item_numbers: list[str]):
    """
    Fetch the quantity on hand for a list of item numbers.
    :param session:
    :param account_id:
    :param item_numbers:
    :return:
    """
    headers = {
        "x-unfi-host-system": "WBS",
        "x-unfi-language": "en-US",
    }
    payload = {
        "itemNumbers": item_numbers,
    }
    session.headers.update(headers)
    endpoint = shopping_customers_items_endpoints["quantity_on_hand"]
    endpoint = endpoint.format(accountID=account_id)
    result = session.post(endpoint, json=payload)
    return result


def fetch_recommended(session, account_id: str, page_number: int = 0,
                      page_size: int = 12):
    """
    Fetch the recommended items for your account based on your order history
    https://www.myunfi.com/shopping/api/customers/001014/items/recommended?page=0&size=12&hostSystem=WBS
    :param session:
    :param account_id:
    :param dc: The DC number to search in.
    :param search_term: The search term to use.
    :param page_number:
    :param page_size:
    :return:
    """
    headers = session.headers.copy()
    headers.update({
        "x-unfi-host-system": "WBS",
        "x-unfi-language": "en-US",
        "accept": "application/json , text/plain, */*"
    })

    session.headers.update(headers)
    endpoint = shopping_customers_items_endpoints["recommended"]
    endpoint = endpoint.format(accountID=account_id)

    result = session.get(endpoint, params={"page": page_number, "size": page_size}, headers=headers)
    return result


def fetch_items(session, account_id: str, dc_num: int, brand_id: str = None, department_ids: list[int] = None,
                category_id=None, sub_category_id=None, search_term="*", page_number: int = 0,
                page_size: int = 96) -> JSONResponse:
    """
    Fetch the items for a given brand.
    https://www.myunfi.com/shopping/api/customers/001014/items/search?brands=40579&dcNumber=6&page=0&searchTerm=%2A&size=12&hostSystem=WBS
    :param session:  The session to use.
    :param account_id:  The account ID to use.
    :param dc_num: Distro center number.
    :param brand_id: brand id
    :param department_ids: department ids to use
    :param search_term:
    :param page_number:
    :param page_size:
    :return:

    """
    headers = {
        "x-unfi-host-system": "WBS",
        "x-unfi-language": "en-US",
        "accept": "application/json , text/plain, */*"
    }

    session.headers.update(headers)
    endpoint = shopping_customers_items_endpoints["search"]
    endpoint = endpoint.format(accountID=account_id)
    params = {
        "dcNumber": dc_num,
        "page": page_number,
        "searchTerm": search_term,
        "size": page_size,
    }
    payload = {}
    if sub_category_id:
        payload["subCategoryId"] = sub_category_id
    if department_ids:
        params["departments"] = ",".join([str(department_id) for department_id in department_ids])
    if brand_id:
        params["brands"] = brand_id
    if payload:
        result = session.post(endpoint, json=payload, params=params)
    else:
        result = session.get(endpoint, params=params)
    return result


def fetch_sub_category_members(session, account_id: str, parent_category_id, sub_category_id: str, page_number: int = 0,
                               page_size: int = 12):
    """
    Fetch all items from a given category
    https://www.myunfi.com/shopping/api/customers/001014/subcategories?parentId=1377&hostSystem=WBS
    :param session:
    :param account_id:
    :param parent_category_id:
    :param sub_category_id:
    :param page_number:
    :param page_size:
    :return:
    """
    payload = {
        "subcategoryId": sub_category_id,
    }

    params = {
        "page": page_number,
        "size": page_size,
        "parentId": parent_category_id,
    }

    headers = session.headers.copy()
    headers.update({
        "x-unfi-host-system": "WBS",
        "x-unfi-language": "en-US",
        "accept": "application/json , text/plain, */*"
    })

    endpoint = shopping_customers_categories_endpoints["items"]

    result = session.get(shopping_customers_categories_endpoints["items"], params=params, json=payload, headers=headers)
