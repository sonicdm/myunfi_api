from __future__ import annotations

from typing import Any, List, Optional, Type

from pydantic import BaseModel, Field, root_validator

from myunfi.http_wrappers.http_adapters import HTTPSession
from myunfi.http_wrappers.responses import HTTPResponse, JSONResponse
from myunfi.models.base import FetchableModel
from myunfi.api.shopping.items import fetch_product


class NetPriceAdjustments(BaseModel):
    volume_discount_dollars: Any = Field(..., alias='volumeDiscountDollars')


class Pricing(BaseModel):
    net_price: float = Field(..., alias='netPrice')
    net_unit_price: float = Field(..., alias='netUnitPrice')
    net_price_adjustments: Optional[NetPriceAdjustments] = Field(alias='netPriceAdjustments')


class Promotion(BaseModel):
    description: str
    discount_type: str = Field(..., alias='discountType')
    id: int
    promotion_number: Any = Field(..., alias='promotionNumber')
    start_date: str = Field(..., alias='startDate')
    end_date: str = Field(..., alias='endDate')
    discount_value: float = Field(..., alias='discountValue')
    required_srp: Any = Field(..., alias='requiredSrp')
    payment_method: Any = Field(..., alias='paymentMethod')
    min_qty: Any = Field(..., alias='minQty')
    max_qty: Any = Field(..., alias='maxQty')
    item_max_qty: Any = Field(..., alias='itemMaxQty')


class Image(BaseModel):
    url: str


class OrderHistoryItem(BaseModel):
    quantity: int
    customer_order_id: int = Field(..., alias='customerOrderId')
    uuid: str
    customer_number: str = Field(..., alias='customerNumber')
    host_system: str = Field(..., alias='hostSystem')
    client_application: str = Field(..., alias='clientApplication')
    submitted_by: str = Field(..., alias='submittedBy')
    po_number: str = Field(..., alias='poNumber')
    order_name: str = Field(..., alias='orderName')
    status: str
    confirmation_number: str = Field(..., alias='confirmationNumber')
    transmission_id: str = Field(..., alias='transmissionId')
    submitted_timestamp: str = Field(..., alias='submittedTimestamp')
    transmitted_timestamp: str = Field(..., alias='transmittedTimestamp')
    delivery_date: str = Field(..., alias='deliveryDate')


class Product(FetchableModel):
    item_number: Optional[str] = Field(None, alias='itemNumber')
    upc: Optional[str] = None
    case_upc: Optional[str] = Field(None, alias='caseUpc')
    extended_description: Optional[str] = Field(None, alias='extendedDescription')
    pack_qty: Optional[int] = Field(None, alias='packQty')
    pack_size: Optional[str] = Field(None, alias='packSize')
    min_order_qty: Optional[int] = Field(None, alias='minOrderQty')
    country_of_origin_code: Optional[int] = Field(None, alias='countryOfOriginCode')
    ingredients: Optional[str] = None
    organic_code: Optional[str] = Field(None, alias='organicCode')
    brand_id: Optional[int] = Field(None, alias='brandId')
    department_id: Optional[int] = Field(None, alias='departmentId')
    category_id: Optional[int] = Field(None, alias='categoryId')
    subcategory_id: Optional[int] = Field(None, alias='subcategoryId')
    is_private_label: Optional[bool] = Field(None, alias='isPrivateLabel')
    status_code: Optional[str] = Field(None, alias='statusCode')
    status_reason_code: Optional[str] = Field(None, alias='statusReasonCode')
    srp: Optional[float] = None
    wholesale_price: Optional[float] = Field(None, alias='wholesalePrice')
    is_monthly_promo: Optional[bool] = Field(None, alias='isMonthlyPromo')
    disco_reason_code: Optional[str] = Field(None, alias='discoReasonCode')
    item_attributes: Optional[List[str]] = Field(None, alias='itemAttributes')
    wholesale_unit_price: Optional[float] = Field(None, alias='wholesaleUnitPrice')
    id: Optional[int] = None
    pack_config: Optional[str] = Field(None, alias='packConfig')
    title: Optional[str] = None
    description: Optional[str] = None
    brand_name: Optional[str] = Field(None, alias='brandName')
    department_name: Optional[str] = Field(None, alias='departmentName')
    category_name: Optional[str] = Field(None, alias='categoryName')
    subcategory_name: Optional[str] = Field(None, alias='subcategoryName')
    is_msi_restricted: Optional[bool] = Field(None, alias='isMsiRestricted')
    pricing: Optional[Pricing] = None
    promotions: Optional[List[Promotion]] = None
    image: Optional[Image] = None
    qty_on_hand: Optional[int] = Field(None, alias='qtyOnHand')
    order_history: Optional[List[OrderHistoryItem]] = Field(None, alias='orderHistory')

    # fetchable config
    account_id: Optional[str] = None
    _required_fields = ["item_number", "account_id"]
    _queryable_fields = ["item_number"]

    @root_validator(pre=True)
    def is_item_dict(cls, values: dict):
        if "items" in values:
            return values["items"][0]
        return values

    def _fetch(self, session: HTTPSession) -> dict:
        result = fetch_product(session, product_code=self.item_number, account_id=self.account_id)
        json_response = result.get_json()
        if "items" in json_response:
            return json_response["items"][0]
        return json_response
