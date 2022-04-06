from __future__ import annotations

import os
import pickle

from myunfi.models.items.product import Products
from myunfi_product_search.workbook import create_excel_workbook, save_wb
from myunfi_product_search.download import download_product_images

from myunfi import MyUNFIClient
refresh_cache = False
product_list = pickle.load(open("products.pickle", "rb"))

if refresh_cache:
    print("Refreshing cache")
    username = os.getenv("MYUNFI_USERNAME")
    password = os.getenv("MYUNFI_PASSWORD")
    client = MyUNFIClient(username, password)
    new_product_list = Products()
    for product in product_list:
        print(f"Refreshing product {product.brand_name} {product.description}")
        new_product_list.append(product.fetch(session=client.session, account_id=client.account_id))
    pickle.dump(new_product_list, open("products.pickle", "wb"))
    product_list = new_product_list
    download_product_images(client, product_list, r"C:\\temp\\product_images")
    # product = list(product_list.products.values())[0]
    # product.image.download(client.session)





wb = create_excel_workbook(product_list)
save_wb(wb, r"C:\\temp\\aq.xlsx")
