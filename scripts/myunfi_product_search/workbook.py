from __future__ import annotations

import sys
from tkinter import messagebox as mb

from typing import Dict, List

from openpyxl import Workbook
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE

from myunfi.models.items.product import Products
from myunfi.utils.collections import normalize_dict
from .logger import logger


def create_excel_workbook(products: Products):
    excel_dicts: dict[str, dict] = {
        product.item_number: normalize_dict(
            product.dict(
                exclude={"order_history", "executed"}
            )
        ) for product in products
    }
    for product_dict in excel_dicts.values():
        promotions = product_dict.get("promotions")
        if promotions:
            promotions = promotions.copy()
            del product_dict["promotions"]
            for promotion in promotions:
                promo_type = promotion.pop("description")
                for key, value in promotion.items():
                    product_dict[f"{promo_type} {key}"] = value
    logger.debug(f"Creating rows list with {len(excel_dicts)} dicts.")
    dict_keys: set = set()
    headers_to_re_index: List[str] = ["upc_no_check", "case_upc", "brand_name", "description", "title", "sub_type",
                                      "pack_size", "pack_qty",
                                      "product_category", "wholesale_price", "wholesale_unit_price", "srp",
                                      "Non-GMO Project Verified", "Organic", "Gluten Free"]
    for d in excel_dicts.values():
        dict_keys.update(list(d.keys()))
    header = list(dict_keys)
    for header_to_re_index in reversed(headers_to_re_index):
        if header_to_re_index in header:
            header.remove(header_to_re_index)
            header.insert(0, header_to_re_index)
    rows = [
        [h.replace("_", " ").title().replace("`", "'").replace("'S", "'s").replace("Upc", "UPC").replace("Srp", "SRP")
         for h in header]]
    row_dicts = []
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
        row_dicts.append(dict(zip(header, row)))

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


def save_wb(wb: Workbook, output_file) -> None:
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
                    f"Could not save workbook to {output_file}. Ending Program",
                )
                sys.exit(1)
        else:
            return
