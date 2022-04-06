from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class NetPriceAdjustments(BaseModel):
    volume_discount_dollars: Optional[Any] = Field(alias='volumeDiscountDollars')


class PricingItem(BaseModel):
    item_number: str = Field(..., alias='itemNumber')
    net_price: float = Field(..., alias='netPrice')
    net_unit_price: float = Field(..., alias='netUnitPrice')
    net_price_adjustments: Optional[NetPriceAdjustments] = Field(alias='netPriceAdjustments')


class Promotion1(BaseModel):
    id: int
    promotion_number: Any = Field(..., alias='promotionNumber')
    start_date: str = Field(..., alias='startDate')
    end_date: str = Field(..., alias='endDate')
    discount_value: float = Field(..., alias='discountValue')
    discount_type: str = Field(..., alias='discountType')
    description: str
    required_srp: Any = Field(..., alias='requiredSrp')
    payment_method: Any = Field(..., alias='paymentMethod')
    min_qty: Any = Field(..., alias='minQty')
    max_qty: Any = Field(..., alias='maxQty')
    item_max_qty: Any = Field(..., alias='itemMaxQty')


class Promotion(BaseModel):
    item_number: str = Field(..., alias='itemNumber')
    promotions: List[Promotion1]


class Pricing(BaseModel):
    pricing: Optional[List[PricingItem]] = None
    promotions: Optional[List[Promotion]] = None
