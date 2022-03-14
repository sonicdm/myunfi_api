from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Page(BaseModel):
    size: int
    number: int
    number_of_elements: int = Field(..., alias='numberOfElements')
    total_elements: int = Field(..., alias='totalElements')
    total_pages: int = Field(..., alias='totalPages')
    is_sorted: bool = Field(..., alias='isSorted')


class InvoiceListingItem(BaseModel):
    item_number: str = Field(..., alias='itemNumber')
    upc_number: str = Field(..., alias='upcNumber')




class InvoiceListing(BaseModel):
    items: List[InvoiceListingItem]
    # orders: List[Order] Not needed just pull values into this model.
    po_number: str = Field(..., alias='poNumber')
    customer_order_number: str = Field(..., alias='customerOrderNumber')
    order_date: str = Field(..., alias='orderDate')
    # end orders

    transaction_type: str = Field(..., alias='transactionType')
    invoice_number: str = Field(..., alias='invoiceNumber')
    customer_number: str = Field(..., alias='customerNumber')
    invoice_date: str = Field(..., alias='invoiceDate')
    delivery_date: str = Field(..., alias='deliveryDate')
    invoice_total_amount: float = Field(..., alias='invoiceTotalAmount')
    invoice_total_cases: int = Field(..., alias='invoiceTotalCases')
    invoice_total_weight: float = Field(..., alias='invoiceTotalWeight')


class Invoices(BaseModel):
    page: Optional[Page] = None
    invoices: Optional[List[InvoiceListing]] = None
