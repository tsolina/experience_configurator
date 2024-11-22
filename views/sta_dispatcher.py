# import tkinter as tk
# from typing import Callable

# class StaDispatcher:
#     _default_root: tk.Tk = None  # Reference to the tkinter root or main thread dispatcher

#     def __init__(self, root: tk.Tk):
#         if self.__class__._default_root is None:  # Ensure only one root is set
#             self.__class__._default_root = root  # Set the reference to the root Tkinter instance
#         else:
#             raise RuntimeError("StaDispatcher._default_root is already initialized.")

#     @classmethod
#     def begin_invoke(cls, callback:Callable):
#         if cls._default_root:
#             cls._default_root.after(0, lambda: (callback(), cls.do_events()))  # Schedule callback on the main thread
#         else:
#             raise RuntimeError("StaDispatcher._default_root is not initialized.")
        
#     @staticmethod
#     def do_events():
#         """Process pending events."""
#         root = StaDispatcher._default_root  # Reference the main tkinter root window.
#         if root:
#             root.update_idletasks()
#             root.update()

import tkinter as tk
from typing import Callable

class StaDispatcher:
    _default_root: tk.Tk = None  # Reference to the tkinter root or main thread dispatcher

    def __init__(self, root: tk.Tk):
        if self.__class__._default_root is None:  # Ensure only one root is set
            self.__class__._default_root = root  # Set the reference to the root Tkinter instance
        else:
            raise RuntimeError("StaDispatcher._default_root is already initialized.")

    @classmethod
    def begin_invoke(cls, callback: Callable):
        """Schedule a callback to run on the main thread."""
        if cls._default_root:
            cls._default_root.after_idle(lambda: cls._execute(callback))  # Use after_idle to prevent overloading
        else:
            raise RuntimeError("StaDispatcher._default_root is not initialized.")

    @staticmethod
    def _execute(callback: Callable):
        """Helper to execute the callback and process pending events."""
        try:
            callback()
        finally:
            StaDispatcher.do_events()

    @staticmethod
    def do_events():
        """Process pending events."""
        root = StaDispatcher._default_root  # Reference the main tkinter root window.
        if root:
            root.update_idletasks()  # Process idle tasks (e.g., geometry updates)
            # Avoid aggressive use of `update`. It should be rarely necessary.
