from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Type

from pydantic import BaseModel, Field, ValidationError, root_validator

from myunfi.http_wrappers.http_adapters import HTTPSession
from myunfi.http_wrappers.responses import HTTPResponse
from myunfi.logger import get_logger

base_logger = get_logger(__name__)


class Page(BaseModel):
    page_size: Optional[int] = Field(12, alias="size")
    page_number: Optional[int] = Field(0, alias="number")
    number_of_elements: Optional[int] = Field(None, alias='numberOfElements')
    total_elements: Optional[int] = Field(None, alias='totalElements')
    total_pages: Optional[int] = Field(None, alias='totalPages')
    is_sorted: Optional[bool] = Field(None, alias='isSorted')
    sort_direction: Optional[str] = "DESC"
    sort_by: Optional[str] = None


class PaginatedModel(Page):
    """
    Base class for all models that are a single page of a result.
    """

    @root_validator(pre=True)
    def validate_page(cls, values: dict) -> dict:
        page = values.get('page')
        if page is None:
            return values
        else:
            values.update(page)
            del values['page']

        return values


class Sessionable:
    """
    Base class for all models that have a session.
    """
    __SESSION: HTTPSession = None

    @classmethod
    def get_session(cls) -> HTTPSession:
        """
        Returns the session for all models.
        """
        return cls.__SESSION

    @classmethod
    def set_session(cls, session: HTTPSession):
        """
        Sets the session for all models.
        """
        cls.__SESSION = session


class QueryParams(BaseModel):
    """
    Base class for all models that have query parameters.
    """
    name: str = None
    value: str = None


class FetchableModel(BaseModel, Sessionable):
    """
    Base class for all models that can be fetched.
    """

    executed: bool = False
    error: str = None
    _queryable_fields: List[str] = []
    _required_fields: List[str] = []
    _params: Optional[QueryParams] = None
    last_fetched: Optional[datetime] = None

    class Config:
        validate_assignment = True

    def fetch(self, session: HTTPSession = None, **kwargs) -> FetchableModel:
        """
        Fetch the model.
        Subclasses should implement the _fetch method to do the actual fetching.
        """
        begin = datetime.now()
        logger = base_logger.getChild(f"{self.__class__.__name__}.fetch")
        logger.debug(f"Fetching model for {self.__class__.__name__}")
        logger.debug(f"required_fields: {self.__get_field_data(self._required_fields)}")
        logger.debug(f"queryable_fields: {self.__get_field_data(self._queryable_fields)}")
        logger.debug(f"params: {self._params}")
        if not all(getattr(self, field) is not None for field in self._required_fields):
            raise ValueError(f"Cannot fetch product without {self._required_fields} set.")
        # session is required for fetching
        if session is None and self.get_session() is None:
            raise ValueError("Cannot fetch product without a session.")

        session = session or self.get_session()
        result = self._fetch(session, **kwargs)
        if result is None:
            return self
        self.executed = True

        # update the model with the result
        try:
            self.update_model(result)
        except Exception as e:
            logger.exception(e)
            self.error = str(e)
            logger.error(f"Failed to update model for {self.__class__.__name__} {result=}")
            raise
        logger.debug(f"Fetched model for {self.__class__.__name__}. Took {datetime.now() - begin}")
        self.last_fetched = datetime.now()
        return self

    def update_model(self, data: dict) -> None:
        """
        Updates the model with the data from the response.
        might be the alias for that field.
        Sorta hacky, hope this works.
        Needs the Config.validate_assignment = True or else it could get weird and force some bad data.
        """
        aliases_to_fields = {mf.alias or mf.name: mf.name for mf in self.__fields__.values()}
        for field, value in data.items():
            if field in aliases_to_fields:
                setattr(self, aliases_to_fields[field], value)
            else:
                # this will throw a validation error if the field is not in the model
                setattr(self, field, value)

    def _fetch(self, session: HTTPSession = None, **kwargs) -> dict:
        """
        Fetch the model.
        """
        raise NotImplementedError("All subclasses must implement the _fetch method.")

    def success(self) -> bool:
        """
        Returns true if the model was fetched successfully.
        """
        ...

    def error_message(self) -> Optional[str]:
        """
        Returns the error message if the model failed to fetch.
        """
        ...

    def is_fetched(self) -> bool:
        """
        Returns true if the model has been fetched.
        """
        return self.last_fetched is not None

    @property
    def queryable_fields(self) -> List[str]:
        """
        Returns the fields that can be queried.
        """
        return self._queryable_fields

    @property
    def required_fields(self) -> List[str]:
        """
        Returns the fields that must be set before fetching.
        """
        return self._required_fields

    @property
    def params(self) -> Optional[QueryParams]:
        """
        Returns the optional query parameters.
        """
        return self._params

    def __get_field_data(self, fields) -> dict:
        """
        :return:
        """
        return {field: getattr(self, field) for field in fields}


class PaginatedFetchableModel(FetchableModel, PaginatedModel):
    """
    Base class for all models that are a single page of a result. allowing for seeking through results.
    """

    def fetch_next_page(self, session: HTTPSession) -> Optional[BaseModel]:
        """
        Fetches the next page of the result.
        """
        ...

    def fetch_previous_page(self, session: HTTPSession) -> Optional[BaseModel]:
        """
        Fetches the previous page of the result.
        """
        ...

    def fetch_all_pages(self, session: HTTPSession) -> List[BaseModel]:
        """
        Fetches all pages of the result.
        """
        ...

    def get_page(self, session: HTTPSession, page_number: int) -> Optional[Type[BaseModel]]:
        """
        Fetches a specific page of the result.
        """
        ...
