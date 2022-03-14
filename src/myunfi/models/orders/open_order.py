from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class OpenOrderLineItem(BaseModel):
    customer_order_item_id: int = Field(..., alias='customerOrderItemId')
    delivery_department: int = Field(..., alias='deliveryDepartment')
    item_number: str = Field(..., alias='itemNumber')
    quantity: int


class OpenOrder(BaseModel):
    customer_order_id: Optional[int] = Field(None, alias='customerOrderId')
    uuid: Optional[str] = None
    customer_number: Optional[str] = Field(None, alias='customerNumber')
    host_system: Optional[str] = Field(None, alias='hostSystem')
    client_application: Optional[str] = Field(None, alias='clientApplication')
    submitted_by: Optional[str] = Field(None, alias='submittedBy')
    po_number: Optional[str] = Field(None, alias='poNumber')
    order_name: Optional[str] = Field(None, alias='orderName')
    confirmation_number: Optional[str] = Field(None, alias='confirmationNumber')
    transmission_id: Optional[str] = Field(None, alias='transmissionId')
    submitted_timestamp: Optional[str] = Field(None, alias='submittedTimestamp')
    transmitted_timestamp: Optional[str] = Field(None, alias='transmittedTimestamp')
    delivery_date: Optional[str] = Field(None, alias='deliveryDate')
    items: Optional[List[OpenOrderLineItem]] = None
    status: Optional[str] = None
    open_order_id: Optional[str] = Field(None, alias='openOrderId')
