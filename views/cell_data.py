from tkinter import ttk
from typing import Callable, Dict, Type, Union

class CellData:
    def __init__(self, widgets:list, 
                 name:str, 
                 row_id:int, 
                 column_id:int, 
                 widget_class:Type[ttk.Widget], 
                 options:Dict[str, str]=None, 
                 bind:Dict[str, Callable]=None, 
                 grid_options:Dict[str, Union[str, int]]=None):
        self.widgets = widgets
        self.name = name
        self.row_id = row_id
        self.column_id = column_id
        self.widget_class = widget_class
        self.options = options if options else {}
        self.bind = bind if bind else {}
        self.grid_options = grid_options if grid_options else {"padx":1, "pady":1}
        self.name_id = f"{name}_{widget_class.__name__}"