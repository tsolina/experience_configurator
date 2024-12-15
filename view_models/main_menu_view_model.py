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

    def look_editor_apply_looks(self):
        self.context.application.apply_looks()

    def look_editor_look_on_selection(self):
        self.context.application.get_applied_material()

    def variant_editor_activate(self):
        self.context.view_main_window.toggle_editors("variant_editor")

    def variant_editor_apply_variant(self):
        self.context.application.apply_variant()

        
    def change_default_saving_location(self):
        app = self.root_model.application

        selected_path = filedialog.askdirectory(
            title="Select the directory that you want to use as the default",
            initialdir=app.registry.base_path
        )

        if selected_path:
            self.context.services.status.status_update(f"folder {selected_path} selected")
            app.registry.base_path = selected_path
        else:
            self.context.services.status.status_update(f"folder selection failed")


    def windows_activate(self, sub_windows_menu:tk.Menu):
        sub_windows_menu.delete(0, tk.END)

        def for_each_window(window:exp.Window, activate_window:Callable[['exp.Window'], None]):        
            sub_windows_menu.add_command(label=window.name(), command=lambda w=window: activate_window(w))
            
        self.context.application.process_project_windows(for_each_window)


    def look_editor_save(self):
        def save_config():
            self.context.application.xml.save_look.save()

        self.context.application.ready(save_config)


    def variant_editor_save(self):
        def save_config():
            self.context.application.xml.save_config.save()

        self.context.application.ready(save_config)

    def variant_editor_load(self):
        def load_config():
            self.context.application.is_loading = True
            self.context.application.xml.load_config.load()
            self.context.application.is_loading = False

        self.context.application.ready(load_config)
