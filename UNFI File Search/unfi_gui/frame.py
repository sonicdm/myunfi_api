from __future__ import annotations
import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controller import Controller
    from model import TkModel
    from container import TkContainer
    from view import View

class TkFrame(tk.Frame):
    def __init__(self, view: 'View', container: 'TkContainer', controller: 'Controller'=None):
        """
        controller: central controller for the application
        container: central container for the application
        model: data model used by this frame
        """
        super().__init__(container)
        self.model = view.model
        self.container = container
        self.controller = controller if controller else  container.controller
        self.view = view
        # self.create_widgets()

    def create_widgets(self):
        pass

    def get_tk_variable(self, name: str):
        return self.model.get_tk_variable(name)

    def store_tk_variable(self, name: str, value: str):
        self.model.store_tk_variable(name, value)

    def get_controller(self) -> 'Controller':
        return self.container.controller

    def get_model(self) -> 'TkModel':
        return self.model

    def get_container(self) -> 'TkContainer':
        return self.container