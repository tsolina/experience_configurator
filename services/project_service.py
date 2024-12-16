from typing import Callable, Optional
import tkinter as tk
from application.application import Application
from application.project import Project
from services.status_service import StatusService

class ProjectService:
    def __init__(self, application:'Application'):
        self.application = application
        self._root:tk.Tk = None
        self._status:'StatusService' = None

    @property
    def status(self) -> 'StatusService':
        if not self._status:
            self._status = self.application.context.services.status
        return self._status

    def ready(self, callback:Callable[['Project'], None]) -> None:
        def on_status(message:str):
            self.application.context.services.status.status_update(message)

        def on_ready():
            if self.application.active_project is None:
                self.application.context.services.status.status_update_error("No project is currently active")
            else:
                callback(self.application.active_project)
        
        self.application.context.services.catia.ready(on_ready, on_status)

    # def ready(self, callback: Callable[['Project'], None]) -> None:
    #     """Ensures the project is ready before executing the callback."""
    #     if self.application.active_project is None:
    #         self.application.context.services.status.status_update_error("No project is currently active")
    #         return

    #     def on_status(message: str):
    #         self.application.context.services.status.status_update(message)

    #     self.application.context.services.catia.catia_ready(lambda _: callback(self.application.active_project), on_status)

    
    def activate_and_get_project(self, on_fail: Callable = None) -> Optional['Project']:
        if not self.application.active_project:
            # Retry after 1 second if no active project
            self._root.after(1000, self.application.projects.activate)
            if on_fail:
                on_fail()
            return None
        return self.application.active_project
    
    def get_active_project(self, root_view:tk.Tk=None) -> Optional['Project']:
        if root_view:
            self._root = root_view
        """Attempts to activate the project, retries on failure, and updates the status."""
        def on_fail():
            self.status.status_update_error("No active project found. Retrying...")
            self._root.after(1000, self.application.projects.activate)

        project = self.activate_and_get_project(on_fail)
        return project