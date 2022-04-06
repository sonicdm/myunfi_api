from __future__ import annotations

import os
import unittest
from pathlib import Path

from myunfi import MyUNFIClient
from myunfi.models.invoices import InvoiceList

this_file_path = Path(__file__)
assets_path = this_file_path.parents[2] / "Assets"
invoices_path = assets_path / "Invoices"
credit_json = invoices_path / "invoice_credit.json"
credits_json = invoices_path / "invoices_credits.json"
invoice_line_item_json = invoices_path / "invoice_line_item.json"
invoices_json = invoices_path / "invoices.json"


class TestCredits(unittest.TestCase):
    def test_credits_from_json(self):
        credits_list = InvoiceList.parse_file(credits_json)
        pass


class TestInvoices(unittest.TestCase):
    def test_invoices_from_json(self):
        invoices_list = InvoiceList.parse_file(invoices_json)
        pass


class TestFetchInvoices(unittest.TestCase):

    def test_invoices_fetch(self):
        client = MyUNFIClient(
            username=os.getenv("MYUNFI_USERNAME"),
            password=os.getenv("MYUNFI_PASSWORD"),
        )
        invoices = InvoiceList(account_id="001014")
        invoices.fetch(client.session)
        pass

    def test_invoices_fetch_from_date(self):
        client = MyUNFIClient(
            username=os.getenv("MYUNFI_USERNAME"),
            password=os.getenv("MYUNFI_PASSWORD"),
        )
        invoices = InvoiceList(account_id="001014", from_date="2022-03-14")
        invoices.fetch(client.session)
        pass

    def test_invoices_fetch_full_invoices(self):
        client = MyUNFIClient(
            username=os.getenv("MYUNFI_USERNAME"),
            password=os.getenv("MYUNFI_PASSWORD"),
        )
        invoices = InvoiceList(account_id="001014", from_date="2022-03-11")
        invoices.fetch(client.session)
        full_invoices = invoices.fetch_invoices()
        pass
