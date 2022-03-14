from __future__ import annotations
from dateutil.parser import parse as parse_date
from datetime import datetime, timedelta
from typing import List, Type, Union

from dateutil.relativedelta import relativedelta

from myunfi.http_wrappers.http_adapters import HTTPRequest, HTTPSession
from ...http_wrappers.responses import ExcelResponse, JSONResponse, PDFResponse
from ..endpoints import shopping_customers_orders_endpoints

"""
    This module contains the order fetching methods for the shopping API.
    
    shopping_customers_orders_endpoints: dict[str,str] = {
        "order_guides": shopping_customers_account_id_order_guides,
        "orders": shopping_customers_account_id_orders,
        "invoices": shopping_customers_account_id_orders_invoices,
        "invoice_id": shopping_customers_account_id_orders_invoices_invoice_id,
        "open_orders": shopping_customers_account_id_orders_open_orders,
        "order_id": shopping_customers_account_id_orders_order_id
    }
    
    # https://www.myunfi.com/shopping/api/customers/001014/openOrders?hostSystem=WBS
    # https://www.myunfi.com/shopping/api/customers/001014/orderGuides?hostSystem=WBS
    # https://www.myunfi.com/shopping/api/customers/001014/orders?hostSystem=WBS
    # https://www.myunfi.com/shopping/api/customers/001014/orders?ordersFromDate=2021-12-09T00%3A00%3A00Z&hostSystem=WBS
    # https://www.myunfi.com/shopping/api/customers/001014/invoices/68646284-006?transactionType=INVOICE&hostSystem=WBS
    # https://www.myunfi.com/shopping/api/customers/001014/invoices?order=invoiceDate&page=0&size=12&sort=DESC&startInvoiceDate=2021-12-08&hostSystem=WBS
    # https://www.myunfi.com/shopping/api/customers/001014/invoices?order=invoiceDate&size=12&sort=DESC&startInvoiceDate=2021-12-08&hostSystem=WBS
    # https://www.myunfi.com/shopping/api/customers/001014/invoices?order=invoiceDate&size=12&sort=DESC&startInvoiceDate=2021-12-11&transactionTypes=INVOICE&hostSystem=WBS
    # https://www.myunfi.com/shopping/api/customers/001014/invoices?order=invoiceDate&size=12&sort=DESC&startInvoiceDate=2021-12-11&transactionTypes=CREDIT&hostSystem=WBS
    # https://www.myunfi.com/shopping/api/customers/001014/invoices?order=invoiceDate&size=12&sort=DESC&startInvoiceDate=2021-12-11&transactionTypes=DEBIT&hostSystem=WBS
    # https://www.myunfi.com/shopping/api/customers/001014/orders/C54DAE6A-E8A9-4ED0-BEFC-5215372DD211?hostSystem=WBS
    
    
"""


def fetch_orders(session: HTTPSession, account_id: int, from_date: Union[str, datetime] = None) -> JSONResponse:
    """
        Fetches all orders for the given customer.
        https://www.myunfi.com/shopping/api/customers/001014/orders?ordersFromDate=2021-12-12T00%3A00%3A00Z&hostSystem=WBS
        Args:
            session: The session to use for the request.
            account_id: The customer ID to fetch orders for.
            from_date: The start date to fetch all orders through todays as a string or datetime object.

        Returns:
            A HTTPResponse object containing the orders.
    """
    if not from_date:
        # default to 3 months ago
        from_date = datetime.today() - relativedelta(months=3)

    endpoint = shopping_customers_orders_endpoints["orders"]
    endpoint = endpoint.format(accountID=account_id)
    assert isinstance(from_date, (str, datetime)), "from_date must be a date string or datetime object."
    if isinstance(from_date, datetime):
        from_date = from_date.replace(hour=0, minute=0, second=0).strftime("%Y-%m-%dT%H:%M:%SZ")
    elif isinstance(from_date, str):
        from_date = parse_date(from_date).replace(hour=0, minute=0, second=0).strftime("%Y-%m-%dT%H:%M:%SZ")

    params = {
        "ordersFromDate": from_date
    }
    request = session.create_request("GET", shopping_customers_orders_endpoints["orders"], params=params)
    response = request.execute()
    if response.status_code == 200:
        return request.get_json()
    else:
        return None


def fetch_order(session: HTTPSession, account_id: int, order_id: str) -> JSONResponse:
    """
        Fetches an order for the given customer.
        https://www.myunfi.com/shopping/api/customers/001014/orders/C54DAE6A-E8A9-4ED0-BEFC-5215372DD211?hostSystem=WBS
        Args:
            session: The session to use for the request.
            account_id: The customer ID to fetch orders for.
            order_id: The order ID to fetch. (This will be a UUID not invoice number)

        Returns:
            A HTTPResponse object containing the order.
    """
    endpoint = shopping_customers_orders_endpoints["order_id"]
    endpoint = endpoint.format(accountID=account_id, orderID=order_id)
    request = session.create_request("GET", endpoint)
    response = request.execute()
    if response.status_code == 200:
        return request.get_json()
    else:
        return None


def fetch_invoices(session: HTTPSession, account_id: int, from_date: Union[str, datetime] = None,
                   transaction_type: str = None, page_size: int = 24, page=0, sort_order: str = "invoiceDate",
                   sort_direction="DESC") -> JSONResponse:
    """
        Fetches all invoices for the given customer account.
        https://www.myunfi.com/shopping/api/customers/001014/invoices?order=invoiceDate&page=0&size=12&sort=DESC&startInvoiceDate=2021-12-08&hostSystem=WBS
        https://www.myunfi.com/shopping/api/customers/001014/invoices?order=invoiceTotalWeight&size=12&sort=DESC&startInvoiceDate=2021-12-11&transactionTypes=INVOICE&hostSystem=WBS
        Args:
            session: The session to use for the request.
            account_id: The customer ID to fetch invoices for.
            from_date: The start date to fetch all invoices through todays as a string or datetime object.
            transaction_type: The type of transaction to fetch.
            page_size: The number of invoices to fetch per page.
            page: The page number to fetch.
            sort_order: The sort order to use. (Default is invoiceDate)
            sort options:
                invoiceDate, invoiceNumber, poNumber, customerOrderNumber, transactionType,
                invoiceTotalAmount, invoiceTotalCases, invoiceTotalWeight
            sort_direction: The sort direction to use. DESC or ASC (Default is DESC)

        Returns:
            A HTTPResponse object containing the invoices.
    """
    if not from_date:
        # default to 3 months ago
        from_date = datetime.today() - relativedelta(months=3)

    endpoint = shopping_customers_orders_endpoints["invoices"]
    endpoint = endpoint.format(accountID=account_id)
    assert isinstance(from_date, (str, datetime)), "from_date must be a date string or datetime object."
    if isinstance(from_date, datetime):
        from_date = from_date.replace(hour=0, minute=0, second=0).strftime("%Y-%m-%dT%H:%M:%SZ")
    elif isinstance(from_date, str):
        from_date = parse_date(from_date).replace(hour=0, minute=0, second=0).strftime("%Y-%m-%dT%H:%M:%SZ")
    if sort_order in ["poNumber", "customerOrderNumber"]:
        sort_order = sort_order + "orders." + sort_order
    params = {
        "order": sort_order,
        "page": page,
        "size": page_size,
        "sort": "DESC",
        "startInvoiceDate": from_date
    }
    if transaction_type:
        params["transactionTypes"] = transaction_type
    request = session.create_request("GET", endpoint, params=params)
    response = request.execute()
    if response.status_code == 200:
        return request.get_json()
    else:
        return None


def fetch_invoice(session: HTTPSession, account_id: int, invoice_number: str,
                  transaction_type: str = "INVOICE",
                  content_type="JSON") -> Union[JSONResponse, ExcelResponse, PDFResponse]:
    """
        Fetches an invoice for the given customer.
        https://www.myunfi.com/shopping/api/customers/001014/invoices/68307090-021?transactionType=INVOICE&hostSystem=WBS
        Args:
            session: The session to use for the request.
            account_id: The customer ID to fetch invoices for.
            invoice_number: The invoice number to fetch. (This will be an invoice number 00000000-000 formatted)
            transaction_type: The type of transaction to fetch. INVOICE,DEBIT,CREDIT (Default is INVOICE)
            content_type: The content type to return the response as. JSON, PDF, or EXCEL (Default is JSON)
        Returns:
            A HTTPResponse object containing the invoice in the given file format.
    """

    content_type_headers = {
        "EXCEL": {"accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
        "PDF": {"accept": "application/pdf"},
        "JSON": {"accept": "application/json; charset=utf-8"}
    }
    content_type = content_type.upper()
    endpoint = shopping_customers_orders_endpoints["invoice_id"]
    endpoint = endpoint.format(accountID=account_id, invoiceID=invoice_number)
    headers = session.headers.copy()
    try:
        headers.update(content_type_headers[content_type])
    except KeyError:
        raise ValueError("content_type must be one of: EXCEL, PDF, JSON")
    request = session.create_request("GET", endpoint, headers=headers)

    response = request.execute()
    if not response.status_code == 200:
        return None

    if content_type == "EXCEL":
        return request.get_excel()
    elif content_type == "PDF":
        return request.get_pdf()
    elif content_type == "JSON":
        return request.get_json()
    else:
        raise ValueError("content_type must be one of: EXCEL, PDF, JSON")
