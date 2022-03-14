from __future__ import annotations, absolute_import
import os
import tkinter as tk
from tkinter import Variable, ttk, filedialog
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from typing import TYPE_CHECKING
from .settings import default_save_path
from .container import TkContainer
from .controller import Controller
from .frame import TkFrame
from .view import View

if TYPE_CHECKING:
    from .search_page import SearchModel, SearchController

if TYPE_CHECKING:
    from unfi_product_search import SearchController
    from search_page import SearchPage

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")


# three page ui for Search, Download Progress, Save/Run Again

class MainContainer(TkContainer):

    def __init__(self, controller: Controller, *args, **kwargs):
        self.base_title = "UNFI API Client"
        super().__init__(controller, self.base_title, *args, **kwargs)


class QueryFrame(tk.Frame):
    def __init__(self, parent: SearchPage, container: tk.Frame, controller: SearchController):
        super().__init__(container)
        self.parent = parent
        self.controller = controller
        self.search_entry = parent.search_entry
        self.search_entry_label = parent.search_entry_label
        self.auto_download_variable = parent.auto_download_variable
        self.search_button: tk.Button = None
        self.create_search_entry_widgets()

    def create_search_entry_widgets(self):
        # multi line text entry box with scrollbar and search button
        search_entry_container = tk.Frame(self)
        search_entry_container.grid(row=0, column=0, sticky="ns", padx=10)
        # search_entry_container.grid_columnconfigure(0, weight=1)
        # search_entry_container.grid_rowconfigure(0, weight=1)
        search_label = tk.Label(
            search_entry_container,
            textvariable=self.search_entry_label,
            font=("Arial", 15),
        )
        search_label.grid(row=0, column=0, sticky="nsew")
        # query entry box
        self.search_entry = ScrolledText(
            search_entry_container,
            height=10,
            width=50,
            wrap=tk.WORD,
        )
        self.search_entry.grid(row=1, column=0, sticky="")

        # action buttons
        button_frame = tk.Frame(search_entry_container)
        button_frame.grid(row=2, column=0, sticky="")
        self.search_button = tk.Button(
            button_frame, text="Search",
            command=lambda: self.parent.do_search(entry=self.search_entry, search_button=self.search_button)
        )
        self.search_button.config(state=tk.DISABLED)
        self.search_button.grid(row=0, column=0, sticky="")
        self.clear_button = tk.Button(
            button_frame, text="Clear", command=self.clear_search_entry
        )
        self.clear_button.grid(row=0, column=1, sticky="")
        # auto download checkbox
        auto_download_checkbox = tk.Checkbutton(
            button_frame,
            text="Auto Download",
            variable=self.auto_download_variable,
        )
        auto_download_checkbox.grid(row=0, column=3, sticky="")

        # enable/disable search button when search entry box gets input
        self.search_entry.bind(
            "<KeyRelease>", lambda x: self.search_entry_key_release()
        )

    def search_entry_key_release(self, event=None):
        # if entry is empty, disable search button
        value = self.search_entry.get("1.0", tk.END).strip()
        if not value:
            self.search_button.config(state=tk.DISABLED)
        else:
            self.search_button.config(state=tk.NORMAL)
            # self.search_variable.set(value)

    def clear_search_entry(self):
        self.search_entry.delete("1.0", tk.END)
        self.search_entry_key_release()


class ProductListFrame(tk.Frame):
    def __init__(self, parent: SearchPage, container: tk.Frame, controller: SearchController=None):
        super().__init__(container)
        self.parent: SearchPage = parent
        self.controller: SearchController = controller
        self.results_listbox_variable: tk.StringVar = parent.results_listbox_variable
        self.results_listbox_label_variable: tk.StringVar = tk.StringVar(self, value="Results:")
        self.save_path_variable: tk.StringVar = parent.save_path_variable
        self.results_listbox: tk.Listbox = None
        self.download_button: tk.Button = None
        self.create_listbox_column_widgets()

    ### listbox functions ###
    def create_listbox_column_widgets(self):
        # list_box_container.grid_columnconfigure(0, weight=1)
        # list_box_container.grid_rowconfigure(0, weight=1)
        list_box_label = tk.Label(
            self,
            textvariable=self.results_listbox_label_variable,
            font=("Arial", 15),
        )
        list_box_label.grid(row=0, column=0, columnspan=2, sticky="nsew")
        # multi select listbox with scrollbar.
        list_box = tk.Listbox(
            self, selectmode=tk.MULTIPLE, height=10, width=100
        )
        self.results_listbox = list_box
        list_box.grid(row=1, column=0, sticky="nsew")
        # enable download button if listbox has items
        list_box.bind(
            "<<ListboxSelect>>", lambda x: self.list_box_select(listbox=list_box)
        )
        scroll_bar = tk.Scrollbar(
            self, orient=tk.VERTICAL, command=list_box.yview
        )
        scroll_bar.grid(row=1, column=1, sticky="wns")
        list_box.config(yscrollcommand=scroll_bar.set)
        scroll_bar.config(command=list_box.yview)
        select_buttons_frame = tk.Frame(self)
        select_buttons_frame.grid(row=2, column=0, columnspan=2, sticky="")

        select_all_button = tk.Button(
            select_buttons_frame,
            text="Select All",
            command=lambda: self.list_box_select_all(list_box),
        )
        select_none_button = tk.Button(
            select_buttons_frame,
            text="Select None",
            command=lambda: self.list_box_deselect_all(list_box),
        )
        select_all_button.grid(row=1, column=0, sticky="")
        select_none_button.grid(row=1, column=1, sticky="")
        remove_button = tk.Button(
            select_buttons_frame,
            text="Remove",
            command=lambda: self.list_box_delete_selection(list_box),
        )
        remove_all_button = tk.Button(
            select_buttons_frame,
            text="Remove All",
            command=lambda: self.list_box_delete_all(list_box),
        )
        remove_button.grid(row=1, column=2, sticky="")
        remove_all_button.grid(row=1, column=3, sticky="")

        self.download_button = tk.Button(
            select_buttons_frame, text="Download", command=lambda: self.parent.do_download(listbox=list_box)
        )
        self.download_button.grid(row=1, column=4, sticky="")

        # disable download button until a product is selected
        self.download_button.config(state=tk.DISABLED)

    def list_box_select(self, listbox: tk.Listbox = None):
        self.download_button.config(state=tk.NORMAL)
        self.selected = [listbox.get(idx) for idx in listbox.curselection()]

    def list_box_deselect(self, listbox: tk.Listbox):
        self.selected = listbox.curselection()
        if len(self.selected) < 1:
            self.download_button.config(state=tk.DISABLED)

    def list_box_select_all(self, listbox: tk.Listbox):
        if self.results_listbox.size() > 0:
            self.download_button.config(state=tk.NORMAL)
        listbox.select_set(0, tk.END)

    def list_box_deselect_all(self, listbox: tk.Listbox):
        self.download_button.config(state=tk.DISABLED)
        listbox.select_clear(0, tk.END)

    def list_box_delete_all(self, listbox: tk.Listbox):
        self.download_button.config(state=tk.DISABLED)
        # self.parent.search_model.results.clear()
        listbox.delete(0, tk.END)

    def list_box_delete_selection(self, listbox: tk.Listbox):
        for i in listbox.curselection():
            desc = listbox.get(i)
            
            listbox.delete(i)
        if self.results_listbox.size() < 1:
            self.download_button.config(state=tk.DISABLED)


class OptionsFrame(tk.Frame):
    def __init__(self, parent: SearchPage, container: tk.Frame):
        super().__init__(container)
        self.parent: SearchPage = parent
        self.save_new_path_variable = parent.save_new_path_variable
        self.save_path_variable = parent.save_path_variable
        self.auto_download_variable = parent.auto_download_variable
        self.auto_save_variable = parent.auto_save_variable
        self.auto_login_variable = parent.auto_login_variable
        self.create_options_frame_widgets()

    ### options frame functions ###
    def create_options_frame_widgets(self):
        options_frame_container = tk.Frame(self)
        options_frame_container.grid(row=1, column=0, sticky="nsew")

        # entry for file save path. using tk.StringVar() to store the path and a file select dialog to select a path
        file_entry_frame = tk.Frame(options_frame_container)
        file_entry_frame.grid(row=0, column=0, sticky="nsew")
        file_entry = tk.Entry(
            file_entry_frame, textvariable=self.save_path_variable, width=40
        )
        file_select_button = tk.Button(
            file_entry_frame, text="Output File: ", command=self.select_save_path
        )
        file_entry.grid(row=0, column=1, columnspan=4, sticky="nsew")
        file_select_button.grid(row=0, column=0, sticky="nsew")
        checkbutton_frame = tk.Frame(options_frame_container)
        checkbutton_frame.grid(row=1, column=0, sticky="nsew")
        save_new_path_checkbutton = tk.Checkbutton(
            checkbutton_frame,
            text="Save New Path",
            variable=self.save_new_path_variable,
        )
        save_new_path_checkbutton.grid(row=0, column=1, sticky="nsew")

        ## make checkbuttons for all options
        auto_save_checkbutton = tk.Checkbutton(
            checkbutton_frame,
            text="Auto Save",
            variable=self.auto_save_variable,
        )
        auto_save_checkbutton.grid(row=0, column=2, sticky="nsew")
        auto_login_checkbutton = tk.Checkbutton(
            checkbutton_frame,
            text="Auto Login",
            variable=self.auto_login_variable,
        )
        auto_login_checkbutton.grid(row=0, column=3, sticky="nsew")
        save_settings_button = tk.Button(
            checkbutton_frame, text="Save Settings", command=self.parent.save_settings
        )
        save_settings_button.grid(row=0, column=5, sticky="nsew")

    def select_save_path(self):
        initial_dir = os.path.dirname(self.save_path_variable.get())
        selected_file = filedialog.asksaveasfile(
            initialdir=initial_dir, defaultextension=".xlsx"
        )
        if not selected_file:
            return
        file_path = selected_file.name
        self.save_path_variable.set(file_path)
