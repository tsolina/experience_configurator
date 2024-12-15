import winreg

class Utility:
    def __init__(self):
        self._list_separator = Utility.get_list_separator()

    @staticmethod
    def get_list_separator() -> str:
        """
        Fetches the list separator from Windows registry (Windows) or defaults.

        Returns:
            str: The list separator.
        """
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\International") as key:
                separator, _ = winreg.QueryValueEx(key, "sList")
            return separator
        except Exception as e:
            print(f"Error fetching list separator: {e}")
            return ","


    @property
    def list_separator(self) -> str:
        """
        Returns the list separator for the current culture.

        Returns:
            str: The list separator.
        """
        return self._list_separator