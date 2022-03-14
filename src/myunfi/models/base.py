from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Type

from pydantic import BaseModel, Field, ValidationError

from myunfi.http_wrappers.http_adapters import HTTPSession
from myunfi.http_wrappers.responses import HTTPResponse


class Page(BaseModel):
    size: int
    number: int
    number_of_elements: int = Field(..., alias='numberOfElements')
    total_elements: int = Field(..., alias='totalElements')
    total_pages: int = Field(..., alias='totalPages')
    is_sorted: bool = Field(..., alias='isSorted')


class PaginatedModel(BaseModel):
    """
    Base class for all models that are a single page of a result.
    """
    page: Page


class Sessionable:
    """
    Base class for all models that have a session.
    """
    __SESSION__: HTTPSession = None

    @classmethod
    def get_session(cls) -> HTTPSession:
        """
        Returns the session for all models.
        """
        return cls.__SESSION__

    @classmethod
    def set_session(cls, session: HTTPSession):
        """
        Sets the session for all models.
        """
        cls.__SESSION__ = session


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

    def fetch(self, session: HTTPSession = None) -> FetchableModel:
        """
        Fetch the model.
        Subclasses should implement the _fetch method to do the actual fetching.
        """
        if not all(getattr(self, field) is not None for field in self._queryable_fields):
            raise ValueError(f"Cannot fetch product without {self._required_fields} set.")
        # session is required for fetching
        if session is None and self.__SESSION__ is None:
            raise ValueError("Cannot fetch product without a session.")

        session = session or self.__SESSION__
        result = self._fetch(session)
        if result is None:
            return self
        self.executed = True

        # update the model with the result
        self.update_model(result)
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



    def _fetch(self, session: HTTPSession) -> dict:
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




class PaginatedFetchAbleModel(FetchableModel, PaginatedModel):
    """
    Base class for all models that are a single page of a result. allowing for seeking through results.
    """

    def _fetch(self, session: HTTPSession) -> HTTPResponse:
        ...

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
