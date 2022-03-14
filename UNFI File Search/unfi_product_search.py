from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable, Dict, List, Union

from unfi_gui.controllers.search import SearchController
# from excel import create_workbook, save_workbook, write_worksheet_rows
from unfi_gui.model import TkModel
from unfi_gui.models.download_model import DownloadModel
from unfi_gui.models.search_model import SearchModel
from unfi_gui.search_page import SearchPage
from unfi_gui.ui import MainContainer
from unfi_gui.view import View

import logging
job_logger = logging.getLogger('jobs')
job_logger.disabled = False
job_logger.level = logging.DEBUG

from unfi_api.api import UnfiAPI
from unfi_api.client import UnfiApiClient

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

def main():
    user = os.environ["UNFI_USER"]
    password = os.environ["UNFI_PASSWORD"]
    unfi_api = UnfiAPI(user, password, incapsula=False)
    client = UnfiApiClient(unfi_api)
    # client = "client"
    search_model = SearchModel
    search_model.set_client(client)
    download_model = DownloadModel
    download_model.set_client(client)
    model = TkModel
    container = MainContainer
    controller = SearchController(container, model, search_model, download_model)
    search_view = View(
        name="search", frame=SearchPage, controller=controller, model=search_model
    )
    # main_view = View(name="main", frame=StartPage, controller=controller)
    controller.register_main_view(search_view)
    controller.register_view(search_view)
    controller.run()


if __name__ == "__main__":
    main()
