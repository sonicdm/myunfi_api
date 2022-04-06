from __future__ import annotations

from datetime import date
from typing import List, Optional, Union
from dateutil.parser import parse as parse_date
from pydantic import BaseModel, Field, root_validator, validator

from myunfi import config
from myunfi.api.shopping.orders import SortBy, fetch_invoices
from myunfi.logger import get_logger
from myunfi.models.base import PaginatedFetchableModel, FetchableModel
from myunfi.models.invoices import Invoice

logger = get_logger(__name__)


#             sort options
#             invoiceDate, invoiceNumber, poNumber, customerOrderNumber, transactionType,
#             invoiceTotalAmount, invoiceTotalCases, invoiceTotalWeight


class InvoiceListingItem(BaseModel):
    item_number: str = Field(..., alias='itemNumber')
    upc_number: str = Field(..., alias='upcNumber')


class InvoiceResult(FetchableModel):
    items: List[InvoiceListingItem]
    # orders: List[Order] Not needed just pull values into this model.
    po_number: str = Field(..., alias='poNumber')
    customer_order_number: str = Field(..., alias='customerOrderNumber')
    order_date: date = Field(..., alias='orderDate')
    # end orders

    transaction_type: str = Field(..., alias='transactionType')
    invoice_number: str = Field(..., alias='invoiceNumber')
    customer_number: str = Field(..., alias='customerNumber')
    invoice_date: date = Field(..., alias='invoiceDate')
    delivery_date: date = Field(..., alias='deliveryDate')
    invoice_total_amount: float = Field(..., alias='invoiceTotalAmount')
    invoice_total_cases: int = Field(..., alias='invoiceTotalCases')
    invoice_total_weight: float = Field(..., alias='invoiceTotalWeight')
    _logger = logger.getChild("InvoiceListing")

    @root_validator(pre=True)
    def orders_to_normal(cls, values):
        validator_logger = cls._logger.getChild("orders_to_normal")
        if "orders" in values:
            orders = values.pop("orders")[0]
            values.update(orders)
        validator_logger.debug(f"{values=}")
        return values

    @validator('invoice_date', 'delivery_date', 'order_date', pre=True)
    def convert_date(cls, v):
        return parse_date(v).date()

    def fetch(self, **kwargs) -> Invoice:
        return Invoice(invoiceNumber=self.invoice_number, transactionType=self.transaction_type).fetch()

    def __repr__(self):
        orig = super().__repr__()
        return f"<MyUNFI Invoice: {self.customer_number} {self.invoice_number} {self.invoice_date} - {orig}>"

    def __str__(self):
        return self.__repr__()


class InvoiceList(PaginatedFetchableModel):
    listings: Optional[List[InvoiceResult]] = Field(None, alias='invoices')
    from_date: Optional[Union[date, str]] = None
    transaction_type: Optional[str] = None
    fetched_invoices: Optional[dict[str, Invoice]] = None
    _logger = logger.getChild("Invoices")
    # fetchable config
    sort_by: str = SortBy.INVOICE_DATE
    dc_number: Optional[int] = config.default_dc
    account_id: Optional[str] = config.default_account_number
    _sort_options: SortBy = SortBy
    _params = ["sort_by", "account_id", "page_number", "page_size"]
    _required_fields = ["account_id"]
    _queryable_fields = ["from_date", "transaction_type"]

    _sortable_fields = [""]

    @property
    def invoices(self):
        return self.fetched_invoices

    def _fetch(self, session=None, **kwargs) -> dict:
        fetch_logger = self._logger.getChild("_fetch")
        fetch_logger.debug(f"_fetch: {kwargs}")
        res = fetch_invoices(
            session,
            account_id=self.account_id,
            from_date=self.from_date,
            transaction_type=self.transaction_type,
            sort_by=self.sort_by,
            page_no=self.page_number,
            page_size=self.page_size,

        )
        data = res.json
        fetch_logger.debug(f"_fetch: {data=}")
        page = data.pop("page")
        data.update(page)

        return data

    def fetch_invoices(self, session=None, **kwargs) -> dict:
        if not session:
            session = self.get_session()
        if not session:
            raise Exception("No session provided")
        fetch_logger = self._logger.getChild("fetch_invoices")
        fetch_logger.debug(f"fetch_invoices: {kwargs}")
        invoices: dict[str, Invoice] = {}
        if len(self.listings) > 0:
            for invoice in self.listings:
                i = Invoice(invoiceNumber=invoice.invoice_number, account_id=self.account_id,
                            transactionType=invoice.transaction_type, from_date=self.from_date)
                i.fetch(session)
                invoices[invoice.invoice_number] = i
        self.fetched_invoices = invoices
        return invoices

    @classmethod
    def search(cls: InvoiceList, from_date=None, transaction_type=None, page_number=None, page_size=None,
               session=None, fetch_results=False, **kwargs) -> InvoiceList:
        session = session or cls.get_session()
        invoice_list = cls()
        invoice_list.from_date = from_date
        invoice_list.transaction_type = transaction_type
        invoice_list.page_number = page_number
        invoice_list.page_size = page_size
        invoice_list.fetch(session, **kwargs)
        if fetch_results:
            invoice_list.fetch_invoices(session, **kwargs)
        return invoice_list
