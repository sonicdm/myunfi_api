from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional, Union

from pydantic import BaseModel, Field, validator

from myunfi import config
from myunfi.api.shopping.items import fetch_items
from myunfi.http_wrappers.http_adapters import HTTPSession
from myunfi.logger import get_logger
from myunfi.models.base import PaginatedFetchableModel
from myunfi.models.items import Product
from myunfi.models.items.product import Products

base_logger = get_logger(__name__)


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
    image: Optional[str]

    @validator('image', pre=True)
    def get_image(cls, v):
        if not isinstance(v, str) and isinstance(v, dict):
            v = v.get('url')
        return v

    def __hash__(self):
        return hash(self.item_number)

    def __eq__(self, other):
        return self.item_number == other.item_number


class SearchResults(PaginatedFetchableModel):
    def _fetch(self, session: HTTPSession = None, **kwargs) -> dict:
        pass

    results: List[ResultItem] = Field([], alias='items')
    products: Optional[Products] = Products()
    dc_number: Optional[int] = config.default_dc
    account_id: Optional[str] = config.default_account_number
    brand_ids: Optional[list[int]] = None
    category_id: Optional[int] = None
    sub_category_id: Optional[int] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None

    _required_fields = ["account_id", "dc_number"]
    _logger = base_logger.getChild(__name__)

    def fetch(self, **kwargs):
        return fetch_items(**kwargs)

    def fetch_products(self, session=None, **kwargs):
        fetched_products: dict[str, Product] = {}
        logger = self._logger.getChild('fetch_products')
        logger.debug(f'Fetching products for {len(self.results)} results')
        for idx, item in enumerate(self.results, 1):
            logger.debug(f'Fetching product for result {idx} of {len(self.results)}')
            item_number = item.item_number
            product = Product(itemNumber=item_number, account_id=self.account_id)
            product.fetch()
            fetched_products[item_number] = product
        if not self.products:
            self.products = Products()
        self.products.update(fetched_products)
        return fetched_products

    def update(self, items: Union[List[ResultItem], dict[str, ResultItem], SearchResults]):
        if isinstance(items, SearchResults):
            self.results.extend(items.results)
            self.results = list(set(self.results))
            self.products.update(items.products)
        elif isinstance(items, list):
            if all(isinstance(item, ResultItem) for item in items):
                self.results.extend(items)
            else:
                collection_types = [type(item) for item in items if not isinstance(item, ResultItem)]
                raise TypeError(f'Expected list of ResultItem, got {collection_types}')
        elif isinstance(items, dict):
            if all(isinstance(item, ResultItem) for item in items.values()):
                self.results.extend(items.values())
            else:
                collection_types = [type(item) for item in items if not isinstance(item, ResultItem)]
                raise TypeError(f'Expected dict of ResultItem, got {collection_types}')

    def __len__(self):
        return len(self.results)

    def __contains__(self, item):
        return item in self.results


class ProductSearch(PaginatedFetchableModel):
    facets: Facets = None
    results: SearchResults = None

    dc_number: Optional[int] = config.default_dc
    account_id: Optional[str] = config.default_account_number
    brand_ids: Optional[list[int]] = None
    category_id: Optional[int] = None
    sub_category_id: Optional[int] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None
    products: Optional[list[Product]] = []
    search_history: Optional[dict[datetime, dict[str, Any]]] = {}
    _params = ["sort_by", "account_id", "page_number", "page_size"]
    _required_fields = ["account_id", "dc_number"]
    _queryable_fields = ["brand_ids", "category_id", "sub_category_id"]

    _sortable_fields = [""]

    def _fetch(self, session: HTTPSession = None, search_term=None, category_id=None, subcategory_id=None,
               brand_ids=None, page=None,
               page_size=None, sort_by=None, sort_order=None, **kwargs) -> dict:
        category_id = category_id or self.category_id
        subcategory_id = subcategory_id or self.sub_category_id
        brand_ids = brand_ids or self.brand_ids
        page = page or self.page_number
        page_size = page_size or self.page_size
        response = fetch_items(self.get_session(), search_term=search_term, account_id=self.account_id,
                               dc_num=self.dc_number,
                               category_id=category_id, sub_category_id=subcategory_id, brand_id=brand_ids,
                               page_number=page, page_size=page_size, sort_by=sort_by, sort_order=sort_order)

        return response.get_json()

    def search(self, search_term=None, category_id=None, subcategory_id=None, brand_ids=None, page=None, page_size=1000,
               fetch_results=False, **kwargs) -> SearchResults:
        category_id = category_id or self.category_id
        subcategory_id = subcategory_id or self.sub_category_id
        brand_ids = brand_ids or self.brand_ids
        page = page or self.page_number
        page_size = page_size or self.page_size
        self.search_history[datetime.now()] = {
            "search_term": search_term, "category_id": category_id,
            "subcategory_id": subcategory_id, "brand_ids": brand_ids, "page": page, "page_size": page_size
        }
        res = self.fetch(search_term=search_term, category_id=category_id, subcategory_id=subcategory_id,
                         brand_ids=brand_ids,
                         page=page, page_size=page_size)

        if self.results:
            self.results.account_id = self.account_id
            self.results.dc_number = self.dc_number
            if fetch_results:
                self.results.fetch_products()
                self.products.extend(self.results.products)
        return self.results

    def update_products_from_results(self, results: SearchResults = None) -> None:
        results = results or self.results
        if results:
            self.products.extend(results.products)
            self.products = list(set(self.products))

    def __bool__(self) -> bool:
        return bool(self.results)
