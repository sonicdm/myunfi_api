from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, root_validator, validator


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
    pallet_name: str = Field(None, alias='palletName')
    # packaging: Packaging place this in the item instead of the packaging model
    eaches: str
    pack: int
    size: str
    unit: str

    regular_case_price: float = Field(None, alias='regularCasePrice')
    regular_srp: float = Field(None, alias='regularSRP')
    net_case_price: float = Field(None, alias='netCasePrice')
    net_each_price: float = Field(None, alias='netEachPrice')
    regular_unit_price: float = Field(None, alias='regularUnitPrice')
    extended_price: float = Field(None, alias='extendedPrice')
    sale_srp: float = Field(None, alias='saleSRP')
    margin: float
    discount: int
    discount_reason: str = Field(None, alias='discountReason')
    item_number: str = Field(None, alias='itemNumber')
    upc_number: str = Field(None, alias='upcNumber')
    line_number: int = Field(None, alias='lineNumber')
    order_quantity: int = Field(None, alias='orderQuantity')
    ship_quantity: int = Field(None, alias='shipQuantity')
    taxed: str
    brand: str
    product_description: str = Field(None, alias='productDescription')
    department: int
    department_name: str = Field(None, alias='departmentName')
    extended_weight: float = Field(None, alias='extendedWeight')
    extended_cube: float = Field(None, alias='extendedCube')

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


class Invoice(BaseModel):
    # validate and get these from the orders list (should only be one item no need for a list or model)
    po_number: Optional[str] = Field(..., alias='poNumber')
    customer_order_number: Optional[str] = Field(..., alias='customerOrderNumber')
    order_date: Optional[date] = Field(..., alias='orderDate')

    ship_to: Optional[ShipTo] = Field(None, alias='shipTo')
    bill_to: Optional[BillTo] = Field(None, alias='billTo')
    line_items: Optional[List[InvoiceLineItem]] = Field(list, alias='items')
    transaction_type: Optional[str] = Field(None, alias='transactionType')
    invoice_number: Optional[str] = Field(None, alias='invoiceNumber')
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
    redempt: Optional[int] = None
    net_total: Optional[int] = Field(None, alias='netTotal')
    total_retail: Optional[int] = Field(None, alias='totalRetail')
    credit_allowance: Optional[int] = Field(None, alias='creditAllowance')
    profit_amount: Optional[int] = Field(None, alias='profitAmount')
    profit_percent: Optional[int] = Field(None, alias='profitPercent')

    @root_validator(pre=True)
    def orders_to_invoice(cls, values):
        orders = values.pop('orders')
        values['poNumber'] = orders[0]['poNumber']
        values['customerOrderNumber'] = orders[0]['customerOrderNumber']
        values['orderDate'] = orders[0]['orderDate']
        return values

    @validator('invoice_date', 'delivery_date', 'order_date', pre=True, always=True)
    def validate_date(cls, value):
        if value is None:
            raise ValueError('Date is required')
        value = datetime.strptime(value, '%Y-%m-%d').date()
        return value
