from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class OpenOrderItem(BaseModel):
    upc: str
    item_number: str = Field(..., alias='itemNumber')
    quantity_ordered: int = Field(..., alias='quantityOrdered')
    quantity_shipped: int = Field(..., alias='quantityShipped')
    sell_unit: str = Field(..., alias='sellUnit')
    pos_status: str = Field(..., alias='posStatus')
    item_description: str = Field(..., alias='itemDescription')
    brand: str
    line_number: int = Field(..., alias='lineNumber')
    line_type: str = Field(..., alias='lineType')


class OpenOrderItems(BaseModel):
    open_order_items: Optional[List[OpenOrderItem]] = Field(
        None, alias='openOrderItems'
    )
