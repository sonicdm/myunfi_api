from __future__ import annotations

import logging
from tkinter import messagebox as mb, simpledialog
from typing import List, TYPE_CHECKING

from tqdm import tqdm
from unfi_api.unfi_web_queries import make_query_list

from myunfi import ProductSearch
from myunfi.models.items.search import SearchResults
from myunfi.utils.threading import threader
from .logger import logger, get_logger
if TYPE_CHECKING:
    from myunfi import MyUNFIClient


query_length_limit = 1737
mod_logger = get_logger(__name__)


def query_chunks_by_character_limit(query: list, max_chars: int) -> List[list[str]]:
    chunks = []
    chunk = []
    for term in query:
        chunk_str = " ".join(chunk)
        if len(chunk_str + " " + term) > max_chars:
            print(f"Chunk: {chunk_str}\nLength: {len(chunk_str)}")
            chunks.append(chunk)
            chunk = [term]
        else:
            chunk.append(term)
    if chunk:
        chunks.append(chunk)
    return chunks


def do_search(query: str, client) -> SearchResults:
    do_search_logger = mod_logger.getChild("do_search")
    searcher = ProductSearch()
    searcher.page_size = 1000
    search_results = SearchResults()

    def __search_chunk(chunk: list):
        # print(f"Searching for {len(chunk)} terms...\n")
        chunk_results = searcher.search(session=client.session, search_term=" ".join(chunk))
        search_results.update(chunk_results)
        # print(f"Search Complete! Found {result.total_hits} items matching the query")
        nonlocal total_results
        nonlocal pbar
        nonlocal total_searched
        total_searched += len(chunk)
        # pbar.desc(f"{total_searched}/{total_results}")
        pbar.update(len(chunk))
        pbar.set_description(f"{total_searched}/{len(query_list)}")
        if chunk_results:
            total_results += len(chunk_results)
        return chunk_results

    total_searched = 0
    total_results = 0
    query_list = make_query_list(query)
    do_search_logger.debug(f"Query list: {query_list}")
    do_search_logger.info(f"Searching for a total of {len(query_list)} terms...")
    chunks = query_chunks_by_character_limit(query_list, query_length_limit)
    with tqdm(total=len(query_list), unit=" terms") as pbar:
        pbar.smoothing = 0.1
        pbar.set_description(f"0/{len(query_list)}")
        results: list[SearchResults] = threader(__search_chunk, chunks, executor_options={"max_workers": 4})

    return search_results


def search_products(query: str, client: MyUNFIClient) -> SearchResults:
    if not query:
        if mb.askyesno("Empty Search", "Your search was empty. Retry?"):
            query = ask_query()
            search_products(query, client)
        else:
            return None

    results = do_search(query, client)
    if results.total_hits < 1:
        return None
    else:
        return results


def ask_query():
    query = simpledialog.askstring("Search For Products", "Search For: ")

    return query
