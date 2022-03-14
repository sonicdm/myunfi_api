from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import Variable
from typing import TYPE_CHECKING, Any, Callable, Dict, List

if TYPE_CHECKING:
    from controller import Controller


class TkModel:
    def __init__(self, controller: 'Controller'):
        self.controller = controller
        self.variables: Dict[str, Variable] = {}
        if not self.__dict__.get('event_types'):
            self.event_types = []
        self.event_handlers: Dict[str:List[Callable]] = {etype: [] for etype in self.event_types}
        
    def register_event_handler(self, key, handler):
        if key in self.event_handlers:
            handlers = self.event_handlers.setdefault(key, [])
            handlers.append(handler)
        else:
            raise KeyError(f'No event type exists for {key}')
        
    def unregister_event_handler(self, key, handler):
        if key in self.event_handlers:
            self.event_handlers[key].remove(handler)

    def trigger_event(self, key, *args):
        if key in self.event_handlers:
            for handler in self.event_handlers[key]:
                handler(*args)
    
    def store_tk_variable(self, key, variable: tk.Variable):
        self.variables[key] = variable

    def get_tk_variable(self, key) -> tk.Variable:
        return self.variables[key]

    def get_variable_value(self, key):
        return self.variables[key].get()

    def set_variable_value(self, key, value):
        self.variables[key].set(value)
