from __future__ import annotations, absolute_import
from typing import TYPE_CHECKING, Callable, List, Union

from unfi_api.product.product import UNFIProduct, UNFIProducts
from ..controller import Controller
from ..container import TkContainer
from ..settings import (
    auto_download,
    auto_login,
    auto_save,
    default_save_path,
    password,
    save_settings,
    search_chunk_size,
    update_settings,
    username,
)

from unfi_api.utils.collections import divide_chunks

if TYPE_CHECKING:
    from unfi_api.search.result import Result, Results
    from ..models.search_model import SearchModel
    from ..models.download_model import DownloadModel
    from ..model import TkModel
    from ..search_page import SearchPage
    from ..ui import ProductListFrame
    
    
class SearchController(Controller):
    def __init__(
            self, container: TkContainer, model: TkModel, search_model: SearchModel, download_model: DownloadModel
    ):
        self.search_model: SearchModel = search_model(self)
        self.download_model: DownloadModel = download_model(self)
        super().__init__("unfi_api_search", container, model)
        # self.search_view = self.container.get_view("search")
        self.search_frame: SearchPage = None
        self.list_box_frame: ProductListFrame = None

    def search(self, query: str, callback: Callable = None) -> Results:
        self.search_model.search(query, callback=callback)

    def download_products(
            self, result: Union[Results, Result], callback=None
    ) -> UNFIProducts:
        return self.download_model.download_products(result, callback)

    def get_downloaded_products(self) -> UNFIProducts:
        return self.download_model.downloaded_products

    def save_workbook(self, products: List[UNFIProduct], callback=None):
        excel_dicts = [product.to_excel_dict() for product in products]
        dict_keys = set(sorted([key for d in excel_dicts for key in d.keys()]))
        
    def get_cancel_button(self) -> None:
        return self.search_frame.cancel_button
    
    def update_progress_bar(self, value: int, max_value: int, message=None):
        self.search_frame.update_progress_bar(value, max_value, message)
    
    def file_save_path(self, path: str) -> None:
        self.get_variable_value("file_save_path", path)
    
    def disable_button(self, button: str) -> None:
        self.search_frame.disable_button(button)
        
    def enable_button(self, button: str) -> None:
        self.search_frame.enable_button(button)
        
    def set_button_command(self, button: str, command: Callable) -> None:
        self.search_frame.set_button_command(button, command)
    
    def set_progress_bar_message(self, message: str) -> None:
        self.get_tk_variable("progress_label").set(message)
        
    def delete_results(self) -> None:
        for product_result in self.search_model.results.product_results:
            del product_result
            
    def get_result_by_list_box_description(self, index: int) -> Result:
        result = self.search_model.list_box_results[index]
    
    def run(self) -> None:
        super().run()