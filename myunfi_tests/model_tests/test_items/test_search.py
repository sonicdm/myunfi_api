from __future__ import annotations
import unittest
import os
from pathlib import Path

from myunfi import MyUNFIClient
from myunfi.models.items.search import ProductSearch

this_file_path = Path(__file__)
assets_path = this_file_path.parents[2] / "Assets"
search_result_json = assets_path / "Items" / "items_search.json"
product_json = assets_path / "Items" / "item.json"


class TestOnlineProductSearch(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = MyUNFIClient(
            username=os.environ.get('MYUNFI_USERNAME'),
            password=os.environ.get('MYUNFI_PASSWORD')
        )

    def test_search_by_name(self):
        search = ProductSearch()
        results = search.search("cider")
        pass

    def test_search_by_name_fetch_results(self):
        search = ProductSearch()
        results = search.search(search_term="bleach", fetch_results=True)
        print(results.products)
        pass


class TestProductSearchResult(unittest.TestCase):

    def test_search_result_parse_from_file(self):
        search = ProductSearch.parse_file(search_result_json)
        results = search.results
