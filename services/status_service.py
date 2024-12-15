import tkinter as tk
from application.application import Application


class StatusService:
    BASE_TITLE = "3DExperience Configurator"

    def __init__(self):
        self._status_message = tk.StringVar()
        self.status_reset()

        self.title_var_prefix = tk.StringVar(value=StatusService.BASE_TITLE)
        self.title_var_dynamic = tk.StringVar(value="")
        self.title_var = tk.StringVar()
        self._update_title_from_var()

        self.title_var_dynamic.trace_add("write", self._update_title_from_var)

    @property
    def status_message(self) -> tk.StringVar:
        """Expose the StringVar for binding to the View."""
        return self._status_message

    def status_update(self, message: str) -> 'StatusService':
        """Update the status message."""
        self._status_message.set(message)
        return self

    def status_update_error(self, message: str) -> 'StatusService':
        """Update the status message."""
        self._status_message.set(f"Error: {message}")
        return self

    def status_reset(self) -> 'StatusService':
        """Reset the status message to a default value."""
        self._status_message.set("Ready")   
        return self



    @property
    def title(self) -> str:
        return self.title_var.get()
    
    @title.setter
    def title(self, value:str):
        if value == self.title_var_dynamic.get():
            return
        
        self.title_var_dynamic.set(value)

    def _update_title_from_var(self, *args) -> None:
        dynamic = self.title_var_dynamic.get()
        combined = f"{self.title_var_prefix.get()} - {dynamic}" if dynamic else self.title_var_prefix.get()
        self.title_var.set(combined)