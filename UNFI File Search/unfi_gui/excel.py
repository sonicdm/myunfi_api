import logging
from typing import Any, Dict, List

from openpyxl import Workbook
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.worksheet.worksheet import Worksheet
from unfi_api.product.product import UNFIProducts

logger = logging.getLogger(__name__)


def create_workbook(tab_name=None) -> Workbook:
    wb = Workbook()
    ws = wb.active
    if tab_name:
        ws.title = tab_name
    return wb


def write_worksheet_rows(ws: Worksheet, rows: list) -> None:
    for row in rows:
        ws.append(row)


def create_workbook_rows(products: UNFIProducts) -> List[Dict[str, Any]]:
    excel_dicts: Dict[str,dict] = products.to_excel()
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
    return rows
    


def save_workbook(wb, filename) -> None:
    wb.save(filename)
