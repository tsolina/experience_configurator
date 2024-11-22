import tkinter as tk

class EntryWithVar(tk.Entry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._value = tk.StringVar()
        self.config(textvariable=self._value)

    @property
    def value(self) -> str:
        return self._value.get()
    
    @value.setter
    def value(self, value:str):
        self._value.set(value)
        