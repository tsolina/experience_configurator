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
        self.context.services.config.change_default_saving_location()


    def windows_activate(self, sub_windows_menu:tk.Menu):
        sub_windows_menu.delete(0, tk.END)

        def for_each_window(window:exp.Window, activate_window:Callable[['exp.Window'], None]):        
            sub_windows_menu.add_command(label=window.name(), command=lambda w=window: activate_window(w))
            
        self.context.application.process_project_windows(for_each_window)


    def look_editor_save(self):
        self.context.services.config.save_look()

    def look_editor_remove_looks(self):
        self.context.application.look.look_editor_remove_looks()

    def variant_editor_save(self):
        self.context.services.config.save_variant()

    def variant_editor_load(self):
        self.context.services.config.load_variant()

