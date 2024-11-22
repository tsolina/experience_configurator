import os
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from application.application import Application

class Log():
    def __init__(self, parent: 'Application'):
        self._parent = parent
        self.application = parent
        self._name = f"Log{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self._folder_path = ""
        self._full_path = ""

    @property
    def Parent(self) -> 'Application':
        return self._parent

    @property
    def Name(self) -> str:
        return self._name

    @Name.setter
    def Name(self, value: str):
        self._name = value    

    def write(self, message: str) -> 'Log':
        # Simulate registry base path as an example; replace with actual registry handling if needed
        base_path = "path/to/your/base"  # Replace with actual base path retrieval
        self._folder_path = os.path.join(base_path, "Log")
        self._full_path = os.path.join(self._folder_path, self._name)

        if not os.path.exists(self._folder_path):
            os.makedirs(self._folder_path)

        with open(self._full_path, 'a') as w:
            w.write(message + "\n")

        return self