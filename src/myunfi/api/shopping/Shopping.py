"""
Main classes for shopping api endpoints.
"""

import logging
import requests

from ..classes import APIEndpointRequestable
from .brands import fetch_brand, fetch_brands_grouped
from .items import fetch_product
from ...config import default_account_number, default_dc
from .orders import fetch_order, fetch_orders, fetch_invoices, fetch_invoice
from ...models.items import Product


class Shopping(APIEndpointRequestable):
    def __init__(self, client=None, session=None, account_id=default_account_number, dc=default_dc):
        super().__init__(client, session, account_id, dc)
        self.items = Items(client, session, account_id, dc)
        # self.content = ShoppingContent(client, session)
        # self.brands = ShoppingBrands(client, session)
        # self.orders = ShoppingOrders(client, session)
        # self.users = ShoppingUsers(client, session)


class Items(APIEndpointRequestable):
    def __init__(self, client=None, session=None, account_id=default_account_number, dc=default_dc):
        super().__init__(client, session, account_id, dc)

    def fetch_item(self, product_code) -> Product:
        res = fetch_product(self.session, product_code, self.account_id, qty_on_hand_supported=True)
        product = Product(**res.get_json())
        return product


class Orders(APIEndpointRequestable):
    def __init__(self, client=None, session=None, account_id=default_account_number, dc=default_dc):
        super().__init__(client, session, account_id, dc)

    def fetch_order(self, order_id):
        res = fetch_order(self.session, order_id, self.account_id)
        order = Order(**res.get_json())
        return order

    def fetch_orders(self, **kwargs):
        res = fetch_orders(self.session, self.account_id, **kwargs)
        orders = Orders(**res.get_json())
        return orders

    def fetch_invoices(self, **kwargs):
        res = fetch_invoices(self.session, self.account_id, **kwargs)
        invoices = Invoices(**res.get_json())
        return res.get_json()

    def fetch_invoice(self, invoice_id):
        res = fetch_invoice(self.session, invoice_id, self.account_id)
        invoice = Invoice(res.get_json())
        return res.get_json()