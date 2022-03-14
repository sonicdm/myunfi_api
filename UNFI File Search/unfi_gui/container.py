from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING, Dict, List

from .exceptions import ViewRequiredException

if TYPE_CHECKING:
    from controller import Controller
    from model import TkModel
    from view import View


class TkContainer(tk.Tk):
    base_title = "Tkinter Container"
    def __init__(self, controller: Controller, title: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller
        self.title(self.base_title)
        # self.geometry("600x600")
        self.resizable(False, False)
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)
        self.views: Dict[str, View] = {}
        self.current_view: View = None
        self.ready = False
        self.cancel = False

    def show_view(self, view_name: str):
        if self.current_view:
            self.current_view.destroy_view()
        self.current_view = self.get_view(view_name)
        self.current_view.raise_view()

    def get_view(self, name: str) -> View:
        return self.views[name]

    def get_model(self, name: str) -> TkModel:
        return self.controller.get_model(name)

    def register_view(self, view: View, controller: Controller = None) -> View:
        controller = controller if controller else self.controller
        view.init_view(self, self.controller)
        self.views[view.name] = view
        return view

    def register_main_view(self, view: View):
        self.main_view = self.register_view(view)
        self.current_view = self.main_view
        self.ready = True

    def show_main_view(self):
        self.show_view(self.main_view.name)

    def unregister_view(self, view_name: str):
        view = self.views.pop(view_name)
        view.destroy_view()

    def get_tk_variable(self, name: str):
        return self.controller.get_tk_variable(name)

    def setup(self, views: List[View] = [], main_view: View = None):
        if main_view:
            self.register_view = main_view
            self.main_view = self.get_view(main_view.name)
        if views:
            self.frames = {}
            for v in views:
                self.register_view(v)
            if "main" not in self.frames and not main_view:
                # default to first view
                self.main_view = self.get_view(views[0].name)

    
    def show_message(self, message_type: str, title:str, message: str):
        message_types = ["info", "warning", "error"]
        if message_type not in message_types:
            raise ValueError(f"message_type must be one of {message_types} not {message_type}")
        if message_type == "error":
            messagebox.showerror(title, message)
        if message_type == "warning":
            messagebox.showwarning(title, message)
        if message_type == "info":
            messagebox.showinfo(title, message)
    
    def run(self):
        if not self.views:
            raise ViewRequiredException("No views registered")
        if not self.main_view:
            raise ViewRequiredException("No main view registered")
        self.main_view.raise_view()
        self.mainloop()

    # def destroy(self) -> None:
    #     self.quit()
    #     self.current_view.destroy_view()
    #     for view in self.views.values():
    #         view.destroy_view()
    #     self.destroy()

    def store_tk_variable(self, name: str, value: str):
        self.controller.store_tk_variable(name, value)
