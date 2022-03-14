from threading import Thread
from typing import Any, Callable, Iterable, Mapping
from unfi_api.search.result import Results


class Search(Thread):
    def __init__(
        self,
        group: None = ...,
        target: Callable[..., Any] | None = ...,
        name: str | None = ...,
        args: Iterable[Any] = ...,
        kwargs: Mapping[str, Any] | None = ...,
        *,
        daemon: bool | None = ...
    ) -> None:
        super().__init__(
            group=group,
            target=target,
            name=name,
            daemon=daemon,
        )
        self.callbacks: dict[str,Callable[..., Any]] = {}
        self.args = args
        self.kwargs = kwargs
        self.results: Results = None
        
    def add_callback(self, event: str, callback: Callable[..., Any]):
        self.callbacks[event] = callback
    
    def set_search_terms(self, search_terms: str):
        self.search_terms = search_terms
        
    def get_results(self):
        return self.results
    
    def do_search(self):
        pass
    
    
