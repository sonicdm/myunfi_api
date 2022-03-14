from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class LineItem(BaseModel):
    upc: Optional[str] = None
    item_number: str = Field(..., alias='itemNumber')
    quantity_ordered: int = Field(..., alias='quantityOrdered')
    quantity_shipped: int = Field(..., alias='quantityShipped')
    sell_unit: Optional[str] = Field(None, alias='sellUnit')
    pos_status: Optional[str] = Field(None, alias='posStatus')
    item_description: Optional[str] = Field(None, alias='itemDescription')
    brand: Optional[str] = None
    line_number: int = Field(..., alias='lineNumber')
    line_type: str = Field(..., alias='lineType')


class OpenOrder(BaseModel):
    order_number: str = Field(..., alias='orderNumber')
    order_type: str = Field(..., alias='orderType')
    po_number: str = Field(..., alias='poNumber')
    submitted_date: str = Field(..., alias='submittedDate')
    delivery_date: str = Field(..., alias='deliveryDate')
    submitted_by: str = Field(..., alias='submittedBy')
    itemoutofstock: str
    items: List[LineItem]


class OpenOrders(BaseModel):
    open_orders: Optional[List[OpenOrder]] = Field(None, alias='openOrders')
