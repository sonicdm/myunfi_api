from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import Variable
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from controller import Controller


class TkModel:
    def __init__(self, controller: 'Controller'):
        self.controller = controller
        self.variables: Dict[str, Variable] = {}

    def store_tk_variable(self, key, variable: tk.Variable):
        self.variables[key] = variable

    def get_tk_variable(self, key) -> tk.Variable:
        return self.variables[key]

    def get_variable_value(self, key):
        return self.variables[key].get()

    def set_variable_value(self, key, value):
        self.variables[key].set(value)
