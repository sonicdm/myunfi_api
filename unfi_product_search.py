from concurrent.futures import thread
import logging
import os
import re
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox as mb
from tkinter import simpledialog
from typing import Dict, List

import openpyxl.utils.exceptions
from openpyxl import Workbook
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.utils.exceptions import IllegalCharacterError
from tqdm import tqdm

from unfi_api import UnfiAPI, UnfiApiClient
from unfi_api.exceptions import exception_retry_prompt
from unfi_api.product import UNFIProduct, UNFIProducts
from unfi_api.search.result import Result, Results
from unfi_api.settings import IMAGE_OUTPUT_PATH, PRODUCT_QUERY_OUTPUT_PATH
from unfi_api.unfi_web_queries import make_query_list, run_query
from unfi_api.utils.collections import divide_chunks
from unfi_api.utils.threading import threader

LOG_TO_CONSOLE = False

log_dir = r"C:\Scriptlogs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_file_name = f"{log_dir}\\{Path(__file__).stem}.log"
output_path = PRODUCT_QUERY_OUTPUT_PATH
image_path = IMAGE_OUTPUT_PATH
description_regex = re.compile(r"(?: at least.*| 100% Organic)", re.IGNORECASE)
FETCH_IMAGES = True
logging.basicConfig(
    filename=log_file_name,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)
if LOG_TO_CONSOLE:
    logger.addHandler(logging.StreamHandler())
    logger.info("Logging to console.")

query_length_limit = 1737

def main():
    logger.info("####################")
    logger.info("Starting UNFI Product Search")
    logger.info("####################")
    user = os.environ.get("UNFI_USER")
    password = os.environ.get("UNFI_PASSWORD")
    tkroot = tk.Tk()
    tkroot.withdraw()
    query = ask_query()
    logger.debug(f"Searching for {query}")

    if query:
        api = init_api(user, password)
        logger.info("Connected!")
        client = UnfiApiClient(api)
        search = True
        products = UNFIProducts()
        fields = set()
        results = Results()
        while True:
            search_results = search_products(query, client)
            results.append_results(search_results.results)
            query = None
            undownloaded_results = results.undownloaded_results()
            if undownloaded_results:
                logger.info(f"Found {undownloaded_results.total_hits} products")
                products.update(download_products(undownloaded_results, client))
                if FETCH_IMAGES:
                    logger.info("Downloading missing images...")
                    download_product_images(client, products, image_path)
                if len(products) > 0:
                    # if mb.askyesno("Run again?", f"{len(products)} products downloaded. Run another search?"):
                    if mb.askyesno("Save Workbook?", f"{len(products)} products downloaded. Save Workbook?"):
                        logger.info("Creating workbook.")
                        print("Creating workbook.")
                        wb = create_excel_workbook(products)
                        print("Saving workbook.")
                        logger.info("Saving workbook.")
                        save_wb(wb, output_path)
                        if mb.askyesno("Workbook Saved.", f"Workbook saved to {output_path}.\n Would you like to do another search?"):
                            query = ask_query()
                            continue
                        else:
                            break
                    elif mb.askyesno("Run again?", f"{len(products)} products downloaded. Run another search?"):
                        query = ask_query()
                        continue
                    else:
                        logger.info("Exiting.")
                        break
                        
            else:
                logging.info("No new results found.")
                if mb.askyesno(
                    "No New Results Found", "No new results found. Do another search?"
                ):
                    query = ask_query()
                else:
                    break

    mb.showinfo("Exiting", "Product Search Complete")
    logger.info("Exiting cleanly.")


def init_api(user, password):
    print("Connecting to UNFI API")
    logger.info("Connecting to UNFI API")
    api = UnfiAPI(user, password, incapsula_retry=False, incapsula=False)
    if api.logged_in:
        logging.info("Logged in!")
        print("Connected!")
        return api
    else:
        logger.error("Login Failed!")
        if mb.askretrycancel(
            "Login Error",
            f"Could not login to UNFI API with username: {user}.",
        ):
            init_api(user, password)
        else:
            logger.error("Could not login to UNFI API. Exiting now.")
            mb.showerror("Login Error", "Could not login to UNFI API. Exiting now.")
            sys.exit(1)

def query_chunks_by_character_limit(query: list, max_chars: int) -> List[str]:
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
    

def do_search(query: str, client: UnfiApiClient) -> Results:
    def __search_chunk(chunk: list):
        # print(f"Searching for {len(chunk)} terms...\n")
        result = client.search(" ".join(chunk))
        # print(f"Search Complete! Found {result.total_hits} items matching the query")
        nonlocal total_results
        nonlocal pbar
        nonlocal total_searched
        total_searched += len(chunk)
        # pbar.desc(f"{total_searched}/{total_results}")
        pbar.update(len(chunk))
        pbar.set_description(f"{total_searched}/{len(query_list)}")
        
        total_results += result.total_hits
        return result
    
    
    total_searched = 0
    total_results = 0
    query_list = make_query_list(query)
    logging.debug(f"Query list: {query_list}")
    print(f"Searching for a total of {len(query_list)} terms...")
    chunks = query_chunks_by_character_limit(query_list, query_length_limit)
    with tqdm(total=len(query_list), unit=" querys") as pbar:
        pbar.smoothing = 0.1
        pbar.set_description(f"0/{len(query_list)}")
        results: List[Result] = threader(__search_chunk, chunks,executor_options={"max_workers": 4})
    product_results = []
    for result in results:
        product_results.extend(result.product_results)
        
    return Results(results=results, product_results=product_results)


def search_products(query: str, client: UnfiApiClient) -> Results:
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


def download_products(results: Results, client: UnfiApiClient) -> UNFIProducts:
    total_dl = 0
    def update_pbar():
        nonlocal total_dl
        total_dl += 1
        pbar.set_description(f"{total_dl}/{len(results)}")
        pbar.update(1)
    print(f"Downloading {len(results.product_results)} products...")
    with tqdm(total=results.total_hits, unit=" products") as pbar:
        pbar.set_description(f"0/{len(results)}")
        pbar.smoothing = 0.1
        products: Dict[str, UNFIProduct] = results.download_products(
            client, lambda x: update_pbar(), threaded=True, thread_count=10
        )
    return products


def download_product_images(
    client: UnfiApiClient, products: UNFIProducts, image_directory: str
):
    print(f"Downloading product images...")
    products_with_images = [x for x in products if x.image_available]
    if not products_with_images:
        return
    max_len = max([len(f"Downloading image for {product.brand} - {product.description}") for product in products_with_images])
    fetched = 0
    with tqdm(total=len(products_with_images), unit=" products",position=0, leave=True) as pbar:
        pbar.set_description(f"Downloading Images for {len(products_with_images)} products...")        
        def _img_fetch(product: UNFIProduct):
            filename = os.path.join(image_directory, f"{product.upc}.jpg")
            if not os.path.exists(filename):
                info = f"Downloading image for {product.brand} - {product.description}"
                logger.info(info)
                # pbar.write(info)
                pbar.set_description(info+" "*(max_len-len(info)))
                with open(filename, "wb") as img_file:
                    image_data = product.get_image(client)
                    if image_data:
                        img_file.write(image_data)
                    nonlocal fetched
                    fetched += 1
            else:
                info = f"Image for {product.brand} - {product.description} already exists."
                pbar.write(info)
                logger.debug(info)
            pbar.update(1)
            # tqdm.write(info)
            
        
        threader(_img_fetch, products_with_images, executor_options={"max_workers": 4})
    logger.info(f"Downloaded {fetched} images.")
    print(f"Downloaded {fetched} images...")
            


def save_wb(wb: Workbook, output_file=output_path) -> None:
    logger.info(f"Saving workbook to {output_file}")
    while True:
        try:
            wb.save(output_file)
            logger.info(f"Saved workbook to {output_file}")
        except PermissionError:
            logger.error(f"Permission Error, could not write to: {output_file}.")
            if mb.askyesno(
                f"Permission Error",
                f"Permission Error, could not write to:\n {output_file}. Retry?",
            ):
                continue
            else:
                mb.showerror(
                    "Save Error",
                    f"Could not save workbook to {output_path}. Ending Program",
                )
                sys.exit(1)
        else:
            return


def ask_query():
    query = simpledialog.askstring("Search For Products", "Search For: ")

    return query


def create_excel_workbook(products: UNFIProducts):

    excel_dicts: List[Dict[str,dict]] = products.to_excel()
    logger.debug(f"Creating rows list with {len(excel_dicts)} dicts.")
    dict_keys: set = set()
    for d in excel_dicts.values():
        dict_keys.update(list(d.keys()))
    header = list(dict_keys)
    rows = [header]
    for product_code, excel_dict in excel_dicts.items():
        row = []
        logger.debug(f"Adding row for {product_code}")
        logger.debug(f"Excel Dict: {excel_dict}")
        for key in header:
            cell = excel_dict.get(key, "")
            if isinstance(cell, str):
                cell = ILLEGAL_CHARACTERS_RE.sub("", cell)
            row.append(cell)
        rows.append(row)
    
    # logger.debug("Rows: {}".format('\n'.join([",".join(str(c for c in row)) for row in rows])))
        

    wb = Workbook()
    ws = wb.active
    logger.debug(f"Writing {len(rows)} rows to workbook.")
    for row in rows:
        try:
            logger.debug(f"Writing row: {row}")
            ws.append(row)
        except Exception as e:
            logger.exception(f"Something went wrong with {row}")
            raise
    return wb


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Something went wrong :(")
        raise
