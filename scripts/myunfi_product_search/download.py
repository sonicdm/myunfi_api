from __future__ import annotations

import os
from typing import Dict

from tqdm import tqdm

from myunfi import MyUNFIClient
from myunfi.models.items.product import Product, Products
from myunfi.models.items.search import ResultItem, SearchResults
from myunfi.utils.threading import threader
from .logger import logger
from .config import IMAGE_OUTPUT_PATH
import hashlib
image_path = IMAGE_OUTPUT_PATH


def download_products(search_results: SearchResults, client: MyUNFIClient) -> Products:
    total_dl = 0
    products = Products()

    def __download(result: ResultItem):
        nonlocal total_dl
        product = Product(itemNumber=result.item_number, account_id=client.account_id)
        product.item_number = result.item_number
        product.account_id = client.account_id
        product.fetch(session=client.session)
        products.append(product)
        total_dl += 1
        pbar.set_description(f"{total_dl}/{len(search_results)}")
        pbar.update(1)
        return product

    logger.info(f"Downloading {len(search_results)} products...")
    with tqdm(total=len(search_results), unit=" products") as pbar:
        pbar.set_description(f"0/{len(search_results)}")
        pbar.smoothing = 0.1
        downloaded_products: list[Product] = threader(__download, search_results.results,
                                                      executor_options={"max_workers": 10})
    return products


def download_product_images(client: MyUNFIClient, products: Products, image_directory: str) -> None:
    print(f"Downloading product images...")

    max_len = max(
        [len(f"Downloading image for {product.brand_name} - {product.description}") for product in products])
    fetched = 0
    with tqdm(total=len(products), unit=" products", position=0, leave=True, ncols=100) as pbar:
        pbar.set_description(f"Downloading Images for {len(products)} products...")

        def _img_fetch(product: Product):
            filename = os.path.join(image_directory, f"{product.upc}.jpg")
            pbar_desc = f"Downloading image for {product.brand_name} - {product.description}"
            logger.info(pbar_desc)
            # pbar.write(info)
            pbar.set_description(pbar_desc + " " * (max_len - len(pbar_desc)))
            image = product.image
            image.download(session=client.session)
            image.save(filename)
            nonlocal fetched
            fetched += 1
            # info = f"Image for {product.brand_name} - {product.description} already exists."
            # pbar.write(info)
            # logger.debug(info)
            pbar.update(1)
    # tqdm.write(info)

    threader(_img_fetch, products, executor_options={"max_workers": 4})



