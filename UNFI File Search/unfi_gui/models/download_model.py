from __future__ import annotations
from typing import TYPE_CHECKING, Callable

from unfi_api.product.product import UNFIProducts
from ..model import TkModel
from unfi_api import UnfiApiClient
from unfi_api.search.result import Results
if TYPE_CHECKING:
    from ..controller import Controller

class DownloadModel(TkModel):
    client: UnfiApiClient = None

    def __init__(self, controller: Controller):
        self.event_types = ["startDownload", "onDownload", "onDownloadComplete", "onDownloadError", "onCancel"]
        super().__init__(controller)
        self.downloaded_products: UNFIProducts = UNFIProducts()
        self.download_queue = []
        cancel_fn = lambda x: controller.cancel_job(x)
        self.register_event_handler("onDownload", self.check_canceled)
        self.job_id = 'download'
        self.cancelled: bool = False
        self.search_model = controller.models['search']

    def check_canceled(self):
        job = self.controller.jobs.get_job(self.job_id)
        self.cancelled = job.job_status == "canceled"

    @classmethod
    def set_client(cls, client: UnfiApiClient):
        cls.client = client

    @classmethod
    def get_client(cls) -> UnfiApiClient:
        return cls.client


    def download_products(self, results: Results, callback: Callable = None, progress_callback: Callable = None, job_id: str = "download"):
        def _dl_callback(x, job_id):
            self.trigger_event("onDownload", job_id)
            if callback:
                callback(x)
        products = results.download_products(self.client, callback=lambda x:_dl_callback(x,job_id), threaded=True, thread_count=10, job_id=self.job_id)
        self.downloaded_products.update(products)
    
    def cancel_download(self):
        pass