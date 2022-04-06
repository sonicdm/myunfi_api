from __future__ import annotations

import re
from typing import Any, Iterator, List, Optional, TYPE_CHECKING, Union

from pydantic import BaseModel, Field, root_validator, validator

from myunfi.api.shopping.items import fetch_product
from myunfi.http_wrappers.http_adapters import HTTPSession
from myunfi.http_wrappers.responses import ImageResponse
from myunfi.models.base import FetchableModel
from myunfi.config import default_account_number, replace_abbreviations
from myunfi.utils.string import replace_abbrs, acronyms_to_uppercase

if TYPE_CHECKING:
    from myunfi.models.items.search import SearchResults

PLACEHOLDER_IMAGE_MD5 = '6dc109b530073c38e107534651b5d6e0'


class NetPriceAdjustments(BaseModel):
    volume_discount_dollars: Optional[Any] = Field(alias='volumeDiscountDollars')


class Pricing(BaseModel):
    net_price: float = Field(..., alias='netPrice')
    net_unit_price: float = Field(..., alias='netUnitPrice')
    net_price_adjustments: Optional[NetPriceAdjustments] = Field(alias='netPriceAdjustments')


class Promotion(BaseModel):
    description: Optional[str]
    discount_type: Optional[str] = Field(alias='discountType')
    id: Optional[int]
    promotion_number: Any = Field(alias='promotionNumber')
    start_date: Optional[str] = Field(alias='startDate')
    end_date: Optional[str] = Field(alias='endDate')
    discount_value: Optional[float] = Field(alias='discountValue')
    required_srp: Optional[Any] = Field(alias='requiredSrp')
    payment_method: Optional[Any] = Field(alias='paymentMethod')
    min_qty: Optional[Any] = Field(alias='minQty')
    max_qty: Optional[Any] = Field(alias='maxQty')
    item_max_qty: Optional[Any] = Field(alias='itemMaxQty')


class Image(BaseModel):
    url: str
    image_md5: Optional[str] = ""
    image_result: Optional[ImageResponse] = None

    class Config:
        arbitrary_types_allowed = True

    def download(self, session: HTTPSession) -> None:
        req = session.create_request("get", url=self.url, stream=True)
        req.execute()
        image_response: ImageResponse = req.get_image()
        self.image_md5 = image_response.md5_hash()
        self.image_result = image_response

    def save(self, path: str) -> None:
        if self.image_result and not self.is_placeholder:
            self.image_result.save_to_file(path)

    @property
    def is_placeholder(self) -> bool:
        """
        This is a placeholder image. This will break if the image ever changes slightly.
        Will not know until its downloaded and you look at the images.
        :return:
        """
        return self.image_md5 == PLACEHOLDER_IMAGE_MD5


class OrderHistoryItem(BaseModel):
    quantity: Optional[int]
    customer_order_id: Optional[int] = Field(None, alias='customerOrderId')
    uuid: Optional[str]
    customer_number: Optional[str] = Field(None, alias='customerNumber')
    host_system: Optional[str] = Field(None, alias='hostSystem')
    client_application: Optional[str] = Field(None, alias='clientApplication')
    submitted_by: Optional[str] = Field(None, alias='submittedBy')
    po_number: Optional[str] = Field(None, alias='poNumber')
    order_name: Optional[str] = Field(None, alias='orderName')
    status: Optional[str]
    confirmation_number: Optional[str] = Field(None, alias='confirmationNumber')
    transmission_id: Optional[str] = Field(None, alias='transmissionId')
    submitted_timestamp: Optional[str] = Field(None, alias='submittedTimestamp')
    transmitted_timestamp: Optional[str] = Field(None, alias='transmittedTimestamp')
    delivery_date: Optional[str] = Field(None, alias='deliveryDate')


class Product(FetchableModel):
    # Descriptors
    brand_name: Optional[str] = Field(None, alias='brandName')
    description: Optional[str] = None
    title: Optional[str] = None
    sub_type: Optional[str] = Field(None, alias='subType')
    extended_description: Optional[str] = Field(None, alias='extendedDescription')

    item_number: Optional[str] = Field(None, alias='itemNumber')
    upc: Optional[int] = None
    upc_no_check: Optional[int] = None
    case_upc: Optional[str] = Field(None, alias='caseUpc')

    category_name: Optional[str] = Field(None, alias='categoryName')
    brand_id: Optional[int] = Field(None, alias='brandId')
    category_id: Optional[int] = Field(None, alias='categoryId')
    country_of_origin_code: Optional[int] = Field(None, alias='countryOfOriginCode')
    country_of_origin_name: Optional[str] = Field(None, alias='countryOfOriginName')
    department_id: Optional[int] = Field(None, alias='departmentId')
    department_name: Optional[str] = Field(None, alias='departmentName')
    disco_reason_code: Optional[str] = Field(None, alias='discoReasonCode')
    id: Optional[int] = None
    image: Optional[Image] = None
    ingredients: Optional[str] = None
    is_monthly_promo: Optional[bool] = Field(None, alias='isMonthlyPromo')
    is_msi_restricted: Optional[bool] = Field(None, alias='isMsiRestricted')
    is_private_label: Optional[bool] = Field(None, alias='isPrivateLabel')
    item_attributes: Optional[List[str]] = Field(None, alias='itemAttributes')
    min_order_qty: Optional[int] = Field(None, alias='minOrderQty')
    order_history: Optional[List[OrderHistoryItem]] = Field(None, alias='orderHistory')
    organic_code: Optional[str] = Field(None, alias='organicCode')
    pack_config: Optional[str] = Field(None, alias='packConfig')
    pack_qty: Optional[int] = Field(None, alias='packQty')
    pack_size: Optional[str] = Field(None, alias='packSize')
    pricing: Optional[Pricing] = None
    promotions: Optional[List[Promotion]] = None
    qty_on_hand: Optional[int] = Field(None, alias='qtyOnHand')
    srp: Optional[float] = None
    status_code: Optional[str] = Field(None, alias='statusCode')
    status_reason_code: Optional[str] = Field(None, alias='statusReasonCode')
    sub_item_number: Optional[str] = Field(None, alias='subItemNumber')
    subcategory_id: Optional[int] = Field(None, alias='subcategoryId')
    subcategory_name: Optional[str] = Field(None, alias='subcategoryName')

    wholesale_price: Optional[float] = Field(None, alias='wholesalePrice')
    wholesale_unit_price: Optional[float] = Field(None, alias='wholesaleUnitPrice')

    # fetchable config
    account_id: Optional[str] = default_account_number
    _required_fields = ["item_number", "account_id"]
    _queryable_fields = ["item_number"]

    @root_validator(pre=True)
    def is_item_dict(cls, values: dict):
        if "items" in values:
            return values["items"][0]
        if "upc" in values:
            if not values["upc"] is None:
                values["upc"] = int(values["upc"])
                values["upc_no_check"] = int(str(values["upc"])[:-1])
        for k, v in values.items():
            if isinstance(v, str):
                values[k] = v.strip().replace("`", "'")
        return values

    @validator('description', 'title', 'sub_type', 'extended_description')
    def description_cleanup(cls, v):
        if v is None:
            return None
        v = re.sub(r"[ ,]og\d,?", " ", v, re.IGNORECASE)
        v = re.sub(r",", ", ", v)
        v = re.sub(r'\s+', ' ', v)
        if replace_abbreviations:
            v = replace_abbrs(v)
        v = acronyms_to_uppercase(v)
        return v.strip().replace("`", "'")

    def _fetch(self, session: HTTPSession = None, **kwargs) -> dict:
        result = fetch_product(session, product_code=self.item_number, account_id=self.account_id)
        json_response = result.get_json()
        if "items" in json_response:
            return json_response["items"][0]
        return json_response

    def download_image(self, session: HTTPSession = None, **kwargs) -> bytes:
        if self.image is None:
            return None
        return self.image.download_image(session, **kwargs)

    def dict(self, exclude: Union[dict, set] = None, **kwargs) -> dict:
        if exclude:
            if isinstance(exclude, dict):
                exclude.update({"item_attributes": True, "image": {"image_result", "image_md5", "image_result"}})
            elif isinstance(exclude, set):
                exclude.add("item_attributes")
        d = super().dict(exclude=exclude, **kwargs)
        d.update({attr: "Y" for attr in self.item_attributes})
        d["product_category"] = self.product_category
        if str(self.organic_code).upper() in ["OG1", "OG2"]:
            d["Organic"] = "Y"
        else:
            d["Organic"] = ""
        return d

    @property
    def product_category(self) -> str:
        return " - ".join([self.department_name, self.category_name, self.subcategory_name])

    def __hash__(self):
        return hash((self.item_number, self.wholesale_price, self.upc))

    def __eq__(self, other):
        return self.item_number == other.item_number and self.wholesale_price == other.wholesale_price and \
               self.upc == other.upc

    def __repr__(self):
        repr_attrs = [self.item_number, self.brand_name, self.title, self.description, self.pack_size,
                      super().__repr__()]
        return f"<Product {' '.join([attr for attr in repr_attrs if attr])}>"

    def __str__(self):
        return self.__repr__()


class Products(BaseModel):
    products: Optional[dict[str, Product]] = {}
    search_results: Optional[list[SearchResults]] = None

    def __repr__(self):
        return f"<Products {len(self.products)} total products.>"

    def __contains__(self, item):
        return item in self.products

    def __iter__(self) -> Iterator[Product]:
        return iter(self.products.values())

    def __getitem__(self, item_code):
        return self.products[item_code]

    def append(self, product: Product):
        if not isinstance(product, Product):
            raise TypeError(f"Product must be of type Product not {type(product)}")
        self.products[product.item_number] = product

    def extend(self, products):
        for product in products:
            self.append(product)

    def update(self, products: Union[Products, List[Product], dict[str, Product]]):
        if isinstance(products, (Products, list)):
            self.extend(products)
        elif isinstance(products, dict):
            self.extend(products.values())
        else:
            raise TypeError(f"Products.update() expects a Products, list, or dict, got {type(products)}")

    def __len__(self):
        return len(self.products)
