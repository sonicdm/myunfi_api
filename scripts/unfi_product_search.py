import logging
import os
import re
import sys
import tkinter as tk
from tkinter import messagebox as mb

from myunfi import MyUNFIClient
from myunfi.models import ProductSearch
from myunfi.models.items.product import Products
from myunfi.models.items.search import SearchResults
from myunfi_product_search.workbook import create_excel_workbook, save_wb
from myunfi_product_search.search import ask_query, do_search
from myunfi_product_search.config import FETCH_IMAGES, PRODUCT_QUERY_OUTPUT_PATH
from myunfi_product_search.download import download_product_images, download_products, image_path
from myunfi_product_search.logger import logger

output_path = PRODUCT_QUERY_OUTPUT_PATH
description_regex = re.compile(r"(?: at least.*| 100% Organic)", re.IGNORECASE)


def main():
    print("####################")
    print("Starting UNFI Product Search")
    print("####################")
    user = os.getenv("MYUNFI_USERNAME")
    password = os.getenv("MYUNFI_PASSWORD")
    tkroot = tk.Tk()
    tkroot.withdraw()
    logger.info("Connecting to MyUNFI")

    client = MyUNFIClient(user, password)

    run(client)


def run(client):
    downloaded_products = Products()
    search = True
    saved = False
    while search:
        search_results: SearchResults = do_query(client)
        if search_results:
            undownloaded_results = SearchResults(
                items=[result for result in search_results.results if
                       result.item_number not in downloaded_products.products]
            )

            if len(undownloaded_results) < 1:
                logger.debug("No new results found.")
                if mb.askyesno("No New Results Found", "No new results found. Do another search?"):
                    continue
                else:
                    if len(downloaded_products) > 0:
                        if not saved:
                            saved = save(downloaded_products)
                        search = False
                        break

            logger.info(f"Found {len(undownloaded_results)} undownloaded products")
            products: Products = download_products(undownloaded_results, client)
            if len(products) > 0:
                saved = False
                logger.info(f"Downloaded {len(products)} products")
                downloaded_products.update(products)

            if not saved and len(downloaded_products) > 0:
                if FETCH_IMAGES:
                    logger.info("Downloading missing images...")
                    download_product_images(client, downloaded_products, image_path)
                saved = save(downloaded_products)
                if mb.askyesno("Search Again?", "Do another search?"):
                    continue
                else:
                    search = False

        elif mb.askyesno("Run again?", f"No new results found. Do another search?"):
            continue
        elif not saved:
            if len(downloaded_products) > 0:
                saved = save(downloaded_products)
            search = False

    # save_wb(wb, output_path)
    mb.showinfo("Exiting", "Product Search Complete")
    # if saved:
    #     logger.info("Saved", "Workbook saved to " + output_path)
    logger.info("Exiting cleanly.")


def save(products: Products) -> bool:
    # ask to save workbook
    if mb.askyesno("Save Workbook?", f"{len(products)} products downloaded. Save Workbook?"):
        logger.info("Creating workbook.")
        # print("Creating workbook.")
        wb = create_excel_workbook(products)
        # print("Saving workbook.")
        # logger.info("Saving workbook.")
        save_wb(wb, output_path)
        return True
    return False


def do_query(client) -> SearchResults:
    search_results = SearchResults()
    query = ask_query()
    while query:
        logger.debug(f"Searching for {query}")
        results: SearchResults = do_search(query, client)
        query = None
        if len(results) > 1:
            # only notify the quantity of NEW results found
            result_count = len(set(results.results).difference(search_results.results))
            search_results.update(results)
            if mb.askyesno("Products Found", f"{result_count} new products found.\nDo you want to search again?"):
                query = ask_query()
    logger.info("Search complete.")
    return search_results


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Got keyboard interrupt. Exiting cleanly.")
        sys.exit(0)
    except Exception as e:
        logger.exception(e)
        logger.error("Exiting with error.")
        raise
