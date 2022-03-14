from __future__ import annotations
import unittest
from myunfi import MyUNFIClient
from myunfi.api.shopping.Shopping import Items
from myunfi.api.shopping.Shopping import Shopping


class TestShoppingItems(unittest.TestCase):
    def test_get_shopping_items(self):
        self.client = MyUNFIClient(
            username='scanning@capellamarket.com',
            password='POSAdmin2489',
        )
        shopping = Items(self.client)
        item = shopping.fetch_item("61003")
        pass