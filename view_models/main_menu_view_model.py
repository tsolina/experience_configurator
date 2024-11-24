from typing import TYPE_CHECKING, Callable
import tkinter as tk
from tkinter import filedialog
from models.main_menu_model import MainMenuModel
import os
import experience as exp
from view_models.application_context import ApplicationContext


if TYPE_CHECKING:
    from view_models.main_window_view_model import MainWindowViewModel


class MainMenuViewModel:
    def __init__(self, context:ApplicationContext):
        self.context = context
        self.root_model = self.context.vm_main_window

    def look_editor_activate(self):
        self.context.view_main_window.toggle_editors("look_editor")

    def variant_editor_activate(self):
        self.context.view_main_window.toggle_editors("variant_editor")
        
    def change_default_saving_location(self):
        app = self.root_model.application

        selected_path = filedialog.askdirectory(
            title="Select the directory that you want to use as the default",
            initialdir=app.registry.base_path
        )

        if selected_path:
            self.root_model.status_update(f"folder {selected_path} selected")
            app.registry.base_path = selected_path
        else:
            self.root_model.status_update(f"folder selection failed")

    def windows_activate(self, sub_windows_menu:tk.Menu):
        print("windows activated")

        def activate_window(window:exp.Window):
            window.activate()
            # print(self.__class__.__name__, window.name(), "activated")
            self.root_model.application.projects.activate()

        def catia_ready():
            sub_windows_menu.delete(0, tk.END)
            for window in self.root_model.application.catia.windows():
                if window.com_type() == "SpecsAndGeomWindow":
                    if not window.name().startswith("VIZ_LOOK_LIBRARY"):
                        sub_windows_menu.add_command(label=window.name(), command=lambda w=window: activate_window(w))


        self.root_model.application.catia_ready(catia_ready)
