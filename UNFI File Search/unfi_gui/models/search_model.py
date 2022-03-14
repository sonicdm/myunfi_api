from re import search
from threading import Thread
from typing import TYPE_CHECKING, Callable, Dict, List
from functools import reduce
from unfi_api import UnfiApiClient
from unfi_api.product import UNFIProduct
from unfi_api.search.result import Result, Results, ProductResult
from unfi_api.utils.jobs import Job
from unfi_api.utils.string import divide_list_into_chunks_by_character_limit
from unfi_api.utils.threading import threader
from ..settings import search_chunk_size
from ..controller import Controller
from ..exceptions import UnfiApiClientNotSetException
from ..model import TkModel
import time
import random

if TYPE_CHECKING:
    from ..controllers.search import SearchController
class SearchModel(TkModel):
    """
    usage:
    """

    client: UnfiApiClient = None

    def __init__(self, controller: Controller, client: UnfiApiClient = None):
        self.event_types = [
            "onSearch",
            "onSearchComplete",
            "onSearchError",
            "onCancel",
            "onSearchStart",
            "onThreadRun",
            "noResults",
        ]
        super().__init__(controller)
        if not self.get_client() and not client:
            raise UnfiApiClientNotSetException("Client not set")
        elif not self.client and client:
            self.client = client
        self.search_terms = []
        self.searched_terms = []
        self.query_length_limit = search_chunk_size
        self.controller: SearchController = controller
        self.results: Results = Results()
        self.search_chunk_size = search_chunk_size
        self.description_to_result_map = {}
        # self.register_event_handler("onSearchComplete", lambda x: controller.stop_cancelled_jobs())

    @classmethod
    def set_client(cls, client: UnfiApiClient):
        cls.client = client

    @classmethod
    def get_client(cls) -> UnfiApiClient:
        return cls.client

    def add_results(self, results: Results) -> None:
        if not self.results:
            self.results = results
        else:
            self.results.extend_results(results)

    def add_result(self, result: Result) -> None:
            self.results.append_result(result)

    def under_query_length_limit(self, query_list: List[str]) -> bool:
        query_str = " ".join(query_list)
        if len(query_str) > self.query_length_limit:
            return False
        return True

    def remove_already_searched_terms(self, terms: List[str]) -> List[str]:
        return list(
            filter(lambda x: x.strip() != "" and x not in self.searched_terms, terms)
        )

    def search(
        self,
        query: str,
        threaded: bool = True,
        callback: Callable = None,
        progress_callback=None,
        job_id="search",
    ) -> Results:
        params = dict(
            query_list=query,
            threaded=threaded,
            callback=callback,
            progress_callback=progress_callback,
            job_id=job_id,
        )

        self.trigger_event("onSearchStart", params)

        searched_count = 0
        found_count = 0
        total_terms = 0
        results = []
        def search_chunk(chunk):
            nonlocal searched_count
            nonlocal found_count
            self.trigger_event("onSearch", chunk)
            searched_count += len(chunk)
            # sleep for random float interval between 0.5 and 1 seconds
            time.sleep(random.uniform(0.5, 1))
            # result = chunk
            result = self.client.search(" ".join(chunk))
            found_count += len(result.product_results)
            self.add_result(result)
            if progress_callback:
                progress_callback(result, searched_count, total_terms, found_count)
            if callback:
                callback(result)
            return result

        query_chunks = self.prepare_query(query)
        if not query_chunks:
            self.controller.set_progress_bar_message("No New Search Terms.. Search Cancelled.")
            return
        # flatten query_chunks and extend self.search_terms
        for chunk in query_chunks:
            self.search_terms.extend(chunk)
        
        # self.search_terms.extend(query_chunks)
        total_terms += reduce(
            lambda count, element: count + len(element), query_chunks, 0
        )
        search_job: Job = self.controller.create_job(
            job_id=job_id,
            job_fn=search_chunk,
            job_data=query_chunks,
            callback=lambda x: self.trigger_event("onSearch", x),
            threaded=threaded,
        )
        self.controller.set_progress_bar_message(
            f"Searching for {total_terms} terms"
        )
        search_job.start()
        self.searched_terms.extend(self.search_terms)
        if search_job.errored():
            self.trigger_event("onSearchError", search_job)
        if search_job.cancelled():
            self.trigger_event("onCancel", search_job)
            pb_message = self.controller.get_variable_value("progress_label")
            self.controller.set_progress_bar_message(pb_message + ": Cancelled search...")
        if search_job.job_output:
            self.searched_terms.extend(self.search_terms)
            # results = search_job.job_output
            # reduce(lambda x, y: self.results.extend(y), results, [])
            found_count = len(self.results.product_results)
            # self.add_results(results)
            self.trigger_event("onSearchComplete", results)
            self.controller.set_progress_bar_message(
                f"Search complete. Found {found_count} results matching the query of {total_terms} terms."
            )
            self.search_terms = []
            
            return self.results
        else:
            self.trigger_event("noResults",  query)
            

    def get_description_mapped_results(self) -> Dict[str, ProductResult]:
        return {
            str(product_result): product_result
            for product_result in self.results.product_results
        }

    def map_description_to_result(self, description: str) -> ProductResult:
        for product_result in self.results.product_results:
            list_val = str(product_result)
            # self.listbox_map = self.search_model.get_description_mapped_results()
            self.description_to_result_map[list_val] = product_result
    
    def get_result_descriptions(self) -> List[str]:
        return [str(result) for result in self.results.product_results]
    
    def get_result_by_description(self, description: str) -> ProductResult:
        return self.description_to_result_map[description]
    
    def delete_result_by_description(self, description: str) -> None:
        product_result = self.get_result_by_description(description)
        self.results.remove_product_result(product_result)
    
    def prepare_query(self,query: str):
        query_split = list(filter(lambda x: str(x).strip() != "", query.split()))
        query_split = list(set(query_split))
        query_list = self.remove_already_searched_terms(query_split)
        duplicate_count = len(query_split) - len(query_list)
        if duplicate_count > 0:
            self.controller.show_message("info", "Duplicates Removed", f"Removed {duplicate_count} terms already searched.")
        if len(query_list) < 1:
            self.controller.show_message("info", "No New Search Terms", "No new search terms found.")
            return []
        
        query_chunks = divide_list_into_chunks_by_character_limit(
                query_list, self.query_length_limit
        )
        return query_chunks