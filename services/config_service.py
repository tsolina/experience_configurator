from typing import Callable
from application.application import Application
from application.project import Project


class ConfigService:
    def __init__(self, application:'Application'):
        self.application = application

    def execute(self, execute_method:Callable[[], None]):
        self.application.context.services.project.ready(lambda _: execute_method())

    def save_look(self):
        self.execute(self.application.xml.save_look.save)

    def save_variant(self):
        self.execute(self.application.xml.save_config.save)

    # def load_variant(self):
    #     self.execute(self._load_config)

    # def _load_config(self):
    #     self.application.is_loading = True
    #     self.application.xml.load_config.load()
    #     self.application.is_loading = False

    def load_variant(self) -> None:
        """Loads the variant configuration."""
        self.execute(lambda: self._set_loading_state(self.application.xml.load_config.load))

    def _set_loading_state(self, load_method: Callable[[], None]) -> None:
        """Handles the loading state while executing the provided method."""
        self.application.is_loading = True
        try:
            load_method()
        finally:
            self.application.is_loading = False