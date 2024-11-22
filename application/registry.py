import winreg

class Registry:
    def __init__(self, i_base='TS_3Dx', i_container='undefined'):
        self._base = i_base
        self._container = i_container

    def path(self):
        return f"Software\\{self._base}\\{self._container}"
    
    def container(self, iContainer):
        self._container = iContainer
        return self
    
    def base(self, iBase):
        self._base = iBase
        return self
    
    def key_save(self, iKey, iValue):
        # Open or create the registry key
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.path()) as key:
            winreg.SetValueEx(key, iKey, 0, winreg.REG_SZ, iValue)
        return self
    
    def key_read(self, iKey):
        try:
            # Open the registry key
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.path(), 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, iKey)
                return value
        except FileNotFoundError:
            return None
        
    def key_delete(self, iKey):
        try:
            # Open the registry key to delete the specific value
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.path(), 0, winreg.KEY_ALL_ACCESS) as key:
                winreg.DeleteValue(key, iKey) # winreg.DeleteKey -> delete entire subkey
        except FileNotFoundError:
            pass  # Handle the case where the key or value doesn't exist
        return self
    
    @classmethod
    def create(cls, i_base='TS_3Dx', i_container='undefined'):
        return cls(i_base, i_container)