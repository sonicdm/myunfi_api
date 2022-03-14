from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class QuantitiesOnHandItem(BaseModel):
    item_number: str = Field(..., alias='itemNumber')
    quantity_on_hand: int = Field(..., alias='quantityOnHand')


class QuantitiesOnHand(BaseModel):
    quantities_on_hand: Optional[List[QuantitiesOnHandItem]] = Field(
        None, alias='quantitiesOnHand'
    )
