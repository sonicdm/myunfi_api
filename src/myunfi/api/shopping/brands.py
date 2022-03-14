"""
Main function file for brands endpoint for shopping.
"""
from requests import Session
from myunfi.http_wrappers import http_adapters
from ..endpoints import shopping_customers_brands_endpoints
from ...http_wrappers.responses import JSONResponse

brands_grouped = shopping_customers_brands_endpoints['brands_grouped']
brands = shopping_customers_brands_endpoints['brands']
brands_base = shopping_customers_brands_endpoints['base']


def fetch_brands_grouped(session: Session, num_per_group=24):
    """
    GET Method
    https://www.myunfi.com/shopping/api/customers/001014/brands/grouped?numPerGroup=24
    :param session:
    :param num_per_group:
    :return:
    """
    header_accept = "accept: application/json, text/plain, */*"
    params = {
        "numPerGroup": num_per_group
    }
    headers = session.headers.copy()
    headers['accept'] = header_accept
    response = session.get(brands_grouped, headers=headers, params=params)
    return JSONResponse(response.status_code, response.content, response.headers)


def fetch_brand(session: Session, brand_id):
    """
    https://www.myunfi.com/shopping/api/customers/001014/brands/40842
    :param session:
    :param brand_id:
    :return:
    """
    header_accept = "accept: application/json, text/plain, */*"
    headers = session.headers.copy()
    headers['accept'] = header_accept
    response = session.get(brands.format(brandID=brand_id), headers=headers)
    return JSONResponse(response.status_code, response.content, response.headers)
