from __future__ import annotations

from collections import OrderedDict
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, root_validator, validator

from myunfi.api.shopping.orders import fetch_invoice
from myunfi.http_wrappers.http_adapters import HTTPSession
from myunfi.models.base import FetchableModel
from myunfi import config

LINE_ITEM_COLUMN_ORDER = {
    'line_number': 1,
    'order_quantity': 2,
    'ship_quantity': 3,
    'eaches': 4,
    'pack': 5,
    'pallet_name': 6,
    'upc': 7,
    'item_number': 8,
    'brand': 9,
    'product_description': 10,
    'taxed': 11,
    'regular_case_price': 12,
    'regular_unit_price': 13,
    'regular_srp': 14,
    'extended_weight': 15,
    'extended_cube': 16,
    'discount': 17,
    'net_case_price': 18,
    'net_each_price': 19,
    'sale_srp': 20,
    'margin': 21,
    'extended_price': 22,
    'discount_reason': 23,
    'department': 24,
    'department_name': 25,
    'size': 26,
    'unit': 27
}


class ShipTo(BaseModel):
    name: str
    street1: str
    street2: str
    city: str
    state: str
    zip_code: str = Field(str, alias='zipCode')
    phone: str


class BillTo(BaseModel):
    name: str
    address1: str
    address2: str
    city: str
    state: str
    zip_code: str = Field(str, alias='zipCode')


class InvoiceLineItem(BaseModel):

    # packaging: Packaging place this in the item instead of the packaging model

    line_number: int = Field(None, alias='lineNumber')
    order_quantity: int = Field(None, alias='orderQuantity')
    ship_quantity: int = Field(None, alias='shipQuantity')
    eaches: str
    pack: int
    pallet_name: str = Field(None, alias='palletName')
    upc: int = Field(None, alias='upcNumber')
    item_number: str = Field(None, alias='itemNumber')
    brand: str
    product_description: str = Field(None, alias='productDescription')
    taxed: str
    regular_case_price: float = Field(None, alias='regularCasePrice')
    regular_unit_price: float = Field(None, alias='regularUnitPrice')
    regular_srp: float = Field(None, alias='regularSRP')
    extended_weight: float = Field(None, alias='extendedWeight')
    extended_cube: float = Field(None, alias='extendedCube')
    discount: float
    net_case_price: float = Field(None, alias='netCasePrice')
    net_each_price: float = Field(None, alias='netEachPrice')
    sale_srp: float = Field(None, alias='saleSRP')
    margin: float
    extended_price: float = Field(None, alias='extendedPrice')
    discount_reason: str = Field(None, alias='discountReason')

    size: str
    unit: str
    department: int
    department_name: str = Field(None, alias='departmentName')

    @root_validator(pre=True)
    def flatten_packaging(cls, values):
        packaging = values.pop('packaging', None)
        if packaging:
            values.update(packaging)
        return values

    @root_validator(pre=True)
    def flatten_pricing(cls, values):
        pricing = values.pop('pricing', None)
        if pricing:
            values.update(pricing)
        return values

    @validator("*", pre=True)
    def trim_strings(cls, value, values, **kwargs):
        if isinstance(value, str):
            return value.strip()
        return value

    def dict(self, **kwargs) -> OrderedDict:
        """
        Returns a dictionary representation of the model in a sorted state for easier output.
        :param kwargs:
        :return:
        """
        original = super().dict(**kwargs)
        ordered = OrderedDict()

        for k, idx in LINE_ITEM_COLUMN_ORDER.items():
            if k in original:
                ordered[k] = original[k]

        for k, v in original.items():
            if k not in ordered:
                ordered[k] = v

        return ordered


class Invoice(FetchableModel):
    invoice_number: Optional[str] = Field(None, alias='invoiceNumber')
    po_number: Optional[str] = Field(None, alias='poNumber')
    customer_order_number: Optional[str] = Field(None, alias='customerOrderNumber')
    # validate and get these from the orders list (should only be one item no need for a list or model)
    order_date: Optional[date] = Field(None, alias='orderDate')
    ship_to: Optional[ShipTo] = Field(None, alias='shipTo')
    bill_to: Optional[BillTo] = Field(None, alias='billTo')
    line_items: Optional[List[InvoiceLineItem]] = Field([], alias='items')
    transaction_type: Optional[str] = Field(None, alias='transactionType')
    customer_number: Optional[str] = Field(None, alias='customerNumber')
    customer_name: Optional[str] = Field(None, alias='customerName')
    invoice_date: Optional[date] = Field(None, alias='invoiceDate')
    delivery_date: Optional[date] = Field(None, alias='deliveryDate')
    deposits: Optional[float] = None
    invoice_total_amount: Optional[float] = Field(None, alias='invoiceTotalAmount')
    invoice_total_cases: Optional[int] = Field(None, alias='invoiceTotalCases')
    invoice_total_weight: Optional[float] = Field(None, alias='invoiceTotalWeight')
    invoice_total_cube: Optional[float] = Field(None, alias='invoiceTotalCube')
    truck_number: Optional[int] = Field(None, alias='truckNumber')
    freight: Optional[float] = None
    fuel_surcharge: Optional[float] = Field(None, alias='fuelSurcharge')
    terms: Optional[str] = None
    master: Optional[str] = None
    distribution_center: Optional[int] = Field(None, alias='distributionCenter')
    non_special: Optional[int] = Field(None, alias='nonSpecial')
    special: Optional[int] = None
    subtotal: Optional[float] = None
    total_discount: Optional[float] = Field(None, alias='totalDiscount')
    tax: Optional[float] = None
    redempt: Optional[float] = None
    net_total: Optional[int] = Field(None, alias='netTotal')
    total_retail: Optional[int] = Field(None, alias='totalRetail')
    credit_allowance: Optional[int] = Field(None, alias='creditAllowance')
    profit_amount: Optional[int] = Field(None, alias='profitAmount')
    profit_percent: Optional[int] = Field(None, alias='profitPercent')

    # fetchable config
    account_id: Optional[str] = config.default_account_number
    _required_fields = ["invoice_number", "account_id", "transaction_type"]
    _queryable_fields = ["invoice_number"]

    @root_validator(pre=True)
    def orders_to_invoice(cls, values):
        if "orders" in values:
            orders = values.pop('orders')
            values['poNumber'] = orders[0]['poNumber']
            values['customerOrderNumber'] = orders[0]['customerOrderNumber']
            values['orderDate'] = orders[0]['orderDate']
        return values

    @validator('invoice_date', 'delivery_date', 'order_date', pre=True, always=True)
    def validate_date(cls, value):
        if value is not None and not isinstance(value, str):
            raise ValueError('Date is required')
        elif isinstance(value, str):
            return datetime.strptime(value, '%Y-%m-%d').date()
        return value

    def _fetch(self, session: HTTPSession) -> dict:
        res = fetch_invoice(session, account_id=self.account_id, invoice_number=self.invoice_number,
                            transaction_type=self.transaction_type)
        js = res.get_json()
        js = self.orders_to_invoice(js)
        return js
        pass

    def __repr__(self):
        original = super().__repr__()
        return f"<Invoice {self.invoice_number}, Total Items: {len(self.line_items)}, " \
               f"Date: {self.invoice_date}, {original}>"

    def __str__(self):
        return self.__repr__()
