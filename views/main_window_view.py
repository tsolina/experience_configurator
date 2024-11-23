import time
from typing import Callable, TYPE_CHECKING
from application.observable_list import ObservableList
import experience as exp
from models.look_editor_model import LookEditorModel
from models.main_menu_model import MainMenuModel
from models.variant_editor_model import VariantEditorModel
from view_models.look_editor_view_model import LookEditorViewModel
from view_models.main_menu_view_model import MainMenuViewModel
from view_models.main_window_view_model import MainWindowViewModel
from view_models.variant_editor_view_model import VariantEditorViewModel
from views.look_editor_view import LookEditorView
from views.main_menu_view import MainMenuView
import tkinter as tk
from tkinter import ttk

from views.sta_dispatcher import StaDispatcher
from views.variant_editor_view import VariantEditorView

if TYPE_CHECKING:
    from application.project import Project

class MainWindowView():
    def __init__(self, root: tk.Tk, view_model: 'MainWindowViewModel'):
        self.root = root
        self.dispatcher = StaDispatcher(root)
        self.view_model = view_model
        self.view_model.dispatcher = self.dispatcher

        self.define_styles(root)
        self.add_status_bar(root)
 
        self.add_main_menu(root)
        # self.current_editor: tk.Frame = None

        self.add_variant_editor(root)
        self.add_look_editor(root)

        # self.add_user_input(root)
        # self.add_options(root)
        # self.execute_frame_definition(root)
        self.view_model.add_title_observer(self.update_root_title)
        self.root.title(self.view_model.title)

        app = self.view_model.application
        app.projects.project_collection.add_observer(self.update_project)
        app.projects.project_collection._notify_observers()

    def update_project(self, projects:ObservableList['Project']):
        for project in projects:
            project.configurations.add_observer(self.look_editor.event_handler.update_treeview)
            project.variants.variant_collection.add_observer(self.variant_editor.update_variant)

    def update_root_title(self, new_title:str):
        self.root.title(new_title)

    def add_main_menu(self, root):
        model = MainMenuModel()
        self.vm_main_menu = MainMenuViewModel(self.view_model, model)
        self.main_menu = MainMenuView(root, self, self.vm_main_menu)

    def define_styles(self, root):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Red.TLabel", foreground="red", font=("Arial", 14), background=root['bg'])

    def add_status_bar(self, root):
        self.status_frame = ttk.Frame(root)
        self.status_frame.pack(side='bottom', fill='x')

        status_title = ttk.Label(self.status_frame, text='Status:', anchor='w', padding=5)
        status_title.pack(side='left')

        self.status_text = ttk.Label(self.status_frame, text='Ready', padding=5, textvariable=self.view_model.status_message)
        self.status_text.pack(side='left', fill='x', expand=True)

        self.version = ttk.Label(self.status_frame, text='0.0.0.1', padding=5) # main.newFeature.internalEdit.bug
        self.version.pack(side='left')

    def add_look_editor(self, root):
        model = LookEditorModel()
        self.vm_look_editor = LookEditorViewModel(model)
        self.look_editor = LookEditorView(root, self, self.vm_look_editor)
        
        self.view_model.look_editor = self.look_editor.look_editor_frame
        self.view_model.current_editor = self.view_model.look_editor

    def add_variant_editor(self, root):
        model = VariantEditorModel()
        self.vm_variant_editor = VariantEditorViewModel(model)
        self.variant_editor = VariantEditorView(root, self, self.vm_variant_editor)
        self.view_model.variant_editor = self.variant_editor.variant_editor_frame

    # @staticmethod
    # def do_events():
    #     """Process pending events."""
    #     root = tk._default_root  # Reference the main tkinter root window.
    #     if root:
    #         root.update_idletasks()
    #         root.update()

    # def sta_thread(self, callback):
    #     """Execute the callback on the main thread."""
    #     self.root.after(0, lambda: (callback(), self.do_events()))

    def sta_thread(self, callback:Callable):
        # time.sleep(2)
        self.dispatcher.begin_invoke(callback)