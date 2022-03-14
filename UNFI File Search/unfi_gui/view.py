from __future__ import annotations
import tkinter as tk
from tkinter.constants import ACTIVE
from typing import TYPE_CHECKING, Dict, List, Optional
from dataclasses import dataclass
from pydantic.main import BaseModel
from .model import TkModel

if TYPE_CHECKING:
    from .controller import Controller
    from .frame import TkFrame
    from .container import TkContainer


@dataclass
class View:
    name: str = None
    frame: TkFrame = None
    model: Optional[TkModel] = None
    view: Optional[TkFrame] = None
    controller: Optional[Controller] = None
    active: bool = False 
    initialized: bool = False
    __model: Optional[TkModel] = None 

    def init_view(self, container: TkContainer, controller: Controller=None, model: TkModel=None) -> None:
        if not controller:
            self.controller = container.controller
        if not isinstance(model, TkModel) and type(model) == TkModel:
            self.model = model(controller=self.controller)
        elif type(model) == TkModel:
            self.model = model(self.controller)
        else:
            self.model = self.controller.model
        self.view = self.frame(self, container, controller)
        self.initialized = True

    def get_model(self, controller: Controller=None) -> TkModel:
        if not controller:
            controller = self.controller
        if not self.__model:
            self.__model = self.model(controller=controller)
        return self.__model

    def raise_view(self) -> None:
        if not self.active:
            self.view.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            self.active = True
        self.view.tkraise()

    def lower_view(self) -> None:
        if self.active:
            self.view.pack_forget()
            self.active = False

    def destroy_view(self) -> None:
        if self.active:
            self.view.pack_forget()
            self.active = False
        self.view.destroy()
    
    








