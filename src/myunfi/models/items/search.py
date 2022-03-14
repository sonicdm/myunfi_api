from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Brand(BaseModel):
    name: str
    count: int
    id: int


class Parent(BaseModel):
    name: str
    id: int


class Category(BaseModel):
    name: str
    count: int
    id: int
    parent: Parent


class DietaryLifestyleItem(BaseModel):
    name: str
    code: str


class MarketingItem(BaseModel):
    name: str
    code: str


class OrganicCode(BaseModel):
    name: str
    code: str


class FreeFromItem(BaseModel):
    name: str
    code: str


class PackConfigCodeItem(BaseModel):
    name: str
    code: str


class Facets(BaseModel):
    brands: List[Brand]
    categories: List[Category]
    dietary_lifestyle: List[DietaryLifestyleItem] = Field(..., alias='dietaryLifestyle')
    marketing: List[MarketingItem]
    organic_codes: List[OrganicCode] = Field(..., alias='organicCodes')
    free_from: List[FreeFromItem] = Field(..., alias='freeFrom')
    pack_config_code: List[PackConfigCodeItem] = Field(..., alias='packConfigCode')


class Page(BaseModel):
    size: int
    number: int
    number_of_elements: int = Field(..., alias='numberOfElements')
    total_elements: int = Field(..., alias='totalElements')
    total_pages: int = Field(..., alias='totalPages')
    is_sorted: bool = Field(..., alias='isSorted')


class Image(BaseModel):
    url: str


class ResultItem(BaseModel):
    id: int
    item_number: str = Field(..., alias='itemNumber')
    upc: str
    pack_qty: int = Field(..., alias='packQty')
    pack_size: str = Field(..., alias='packSize')
    brand_id: int = Field(..., alias='brandId')
    status_code: str = Field(..., alias='statusCode')
    status_reason_code: str = Field(..., alias='statusReasonCode')
    pack_config: str = Field(..., alias='packConfig')
    is_dsd_restricted: bool = Field(..., alias='isDsdRestricted')
    description: str
    brand_name: str = Field(..., alias='brandName')
    title: str
    department_id: int = Field(..., alias='departmentId')
    department_name: str = Field(..., alias='departmentName')
    # no model needed for this field just a str
    image: str


class Results(BaseModel):
    page: Page
    items: List[ResultItem]


class SearchResult(BaseModel):
    facets: Facets = None
    results: Results = None
