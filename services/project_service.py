from typing import Callable
from application.application import Application
from application.project import Project

class ProjectService:
    def __init__(self, application:'Application'):
        self.application = application

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