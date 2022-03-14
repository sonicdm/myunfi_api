from __future__ import annotations
import unittest
from datetime import date
from pathlib import Path
from myunfi.models.invoices import Invoice, Invoices
from myunfi.models.invoices.invoice import InvoiceLineItem

this_file_path = Path(__file__)
assets_path = this_file_path.parents[2] / "Assets"
invoices_path = assets_path / "Invoices"
credit_json = invoices_path / "invoice_credit.json"
credits_json = invoices_path / "invoices_credits.json"
invoice_line_item_json = invoices_path / "invoice_line_item.json"


class TestCredit(unittest.TestCase):
    def test_credit_from_json(self):
        credit = Invoice.parse_file(credit_json)
        self.assertEqual(credit.transaction_type, "CREDIT")
        self.assertEqual(credit.invoice_number, "62448068-001")
        self.assertEqual(credit.invoice_date, date(2022, 3, 2))
        self.assertEqual(credit.delivery_date, date(2022, 3, 4))
        self.assertEqual(credit.po_number, "030222")
        self.assertEqual(credit.customer_order_number, "62448068")
        self.assertEqual(credit.order_date, date(2022, 3, 2))

    def test_credit_line_items(self):
        credit = Invoice.parse_file(credit_json)
        line_items = credit.line_items
        self.assertIsInstance(line_items, list)
        for line_item in line_items:
            self.assertIsInstance(line_item, InvoiceLineItem)


class TestCredits(unittest.TestCase):
    def test_credits_from_json(self):
        credits_list = Invoices.parse_file(credits_json)
        page = credits_list.page





class TestLineItem(unittest.TestCase):
    def test_line_item(self):

        test_line_item: InvoiceLineItem = InvoiceLineItem.parse_file(invoice_line_item_json)
        self.assertEqual(test_line_item.upc_number, "93966510157")
        self.assertEqual(test_line_item.product_description, "OG2 O.V. WHOLE MILK")
        self.assertEqual(test_line_item.department_name, "SUPPLEMENTS")
        self.assertEqual(test_line_item.order_quantity, 0)
        self.assertEqual(test_line_item.ship_quantity, 0.0)
        self.assertEqual(test_line_item.regular_case_price, 28.36)
        self.assertEqual(test_line_item.regular_srp, 6.59)
        self.assertEqual(test_line_item.net_case_price, 28.36)