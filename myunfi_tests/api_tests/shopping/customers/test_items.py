from __future__ import annotations

import json
import os
from unittest import TestCase

import requests

from myunfi.api.shopping.items import fetch_product, fetch_qty_on_hand, fetch_recommended, fetch_items
from myunfi.client.login import do_login


class TestItems(TestCase):

    @classmethod
    def setUpClass(cls):
        print("Logging in...", end="")
        username = os.getenv("MYUNFI_USERNAME")
        password = os.getenv("MYUNFI_PASSWORD")
        password = "POSAdmin2489"
        cls.session = requests.Session()
        logged_in = do_login(cls.session, username, password)
        assert logged_in, "Login failed"
        print("OK!")

    def test_fetch_product(self):
        session = self.session
        product_result = fetch_product(session, "61003", "001014")
        item_dict = product_result.json()
        print(f'Test Fetch Product: {json.dumps(item_dict, indent=4)}')
        pass

    def test_fetch_qty_on_hand(self):
        session = self.session
        items = ["21050", "21559", "61003"]
        qty_on_hand_result = fetch_qty_on_hand(session, "001014", items)
        qty_on_hand_dict = qty_on_hand_result.json()
        print(f'Test Fetch Qty On Hand: {json.dumps(qty_on_hand_dict, indent=4)}')
        pass

    def test_fetch_recommended_items(self):
        session = self.session
        recommended_result = fetch_recommended(session, "001014")
        recommended_dict = recommended_result.json()
        print(f'Test Fetch Recommended: {json.dumps(recommended_dict, indent=4)}')
        pass

    def test_fetch_brand_items(self):
        session = self.session
        brand_result = fetch_items(session, "001014", 6, brand_id="40579")
        brand_dict = brand_result.json()
        print(f'Test Fetch Items by Brand: {json.dumps(brand_dict, indent=4)}')

    def test_search_in_brand(self):
        session = self.session
        search_result = fetch_items(session, "001014", 6, brand_id="31746", search_term="deodorant")
        search_dict = search_result.json()
        print(f'Test Search in Brand: {json.dumps(search_dict, indent=4)}')

    def test_fetch_category_items(self):
        session = self.session
        category_result = fetch_items(session, "001014", 6, category_id="11")
        category_dict = category_result.json()
        print(f'Test Fetch Items by Category: {json.dumps(category_dict, indent=4)}')
