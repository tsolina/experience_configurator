import os
from application.registry import Registry

class RegistryConfig(Registry):
    _container = "VizConfigurator"

    def __init__(self):
        super().__init__()
        self.container(self._container)
        self._base_path = None

    @property
    def base_path(self):
        # Read the base path from the registry if not already loaded
        if self._base_path is None:
            self._base_path = self.key_read("BasePath")
            if not self._base_path:
                # If BasePath is not set, use the default Application Data folder
                appdata = os.getenv('APPDATA')
                self._base_path = os.path.join(appdata, self._container)
                # Ensure the directory exists
                os.makedirs(self._base_path, exist_ok=True)
                # Save to registry
                self.key_save("BasePath", self._base_path)
        return self._base_path

    @base_path.setter
    def base_path(self, value):
        self._base_path = value
        self.key_save("BasePath", self._base_path)  