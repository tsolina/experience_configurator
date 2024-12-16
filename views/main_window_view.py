import time
from typing import Callable, TYPE_CHECKING, Dict
from application.observable_list import ObservableList
import experience as exp
from models.look_editor_model import LookEditorModel
from models.main_menu_model import MainMenuModel
from models.variant_editor_model import VariantEditorModel
from view_models.application_context import ApplicationContext
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
    def __init__(self, root: tk.Tk, context:ApplicationContext):
        self.root = root
        self.context = context
        self.context.view_main_window = self
        self.dispatcher = StaDispatcher(root)
        self.view_model = self.context.vm_main_window
        self.context.vm_main_window.dispatcher = self.dispatcher

        self.define_styles(root)
        self.add_status_bar(root)
 
        self.add_main_menu(root)
        self.editors:Dict[str, tk.Frame] = {}
        self.add_variant_editor(root)
        self.add_look_editor(root)

        self.root.title(self.context.services.status.title)

    def add_main_menu(self, root):
        self.main_menu = MainMenuView(root, self.context)

    def define_styles(self, root):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Red.TLabel", foreground="red", font=("Arial", 14), background=root['bg'])
        style.configure("Standard.TLabel", background=root['bg'])
        style.configure("Custom.TFrame", background="orange", borderwidth=2, relief='solid', padx=2, pady=2)
        style.configure("Standard.TFrame", background=root['bg'])
        style.configure("Option.TFrame", background=root['bg'])
        style.configure("Hover.Option.TFrame", background="#f5f5f5", borderwidth=0)
        style.configure("Selected.Option.TFrame", background="#f0f0f0", borderwidth=0)
        style.configure("Option.TLabel", background=root['bg'])
        style.configure("Hover.Option.TLabel", borderwidth=1, relief='sunken', highlightcolor="#f0f0f0") # "#D9E2E8")
        style.configure("Selected.Option.TLabel", background="#f0f0f0", borderwidth=0)
        style.configure("Standard.TRadiobutton", background=root['bg'])


    def add_status_bar(self, root):
        self.status_frame = ttk.Frame(root)
        self.status_frame.pack(side='bottom', fill='x')

        status_title = ttk.Label(self.status_frame, text='Status:', anchor='w', padding=5)
        status_title.pack(side='left')

        self.status_text = ttk.Label(self.status_frame, text='Ready', padding=5, textvariable=self.context.services.status.status_message)
        self.status_text.pack(side='left', fill='x', expand=True)
        self.context.services.status.status_message.trace_add("write", lambda *args: self.status_text.update_idletasks())

        self.version = ttk.Label(self.status_frame, text='0.0.0.1', padding=5) # main.newFeature.internalEdit.bug
        self.version.pack(side='left')

    def add_look_editor(self, root):
        self.look_editor = LookEditorView(root, self.context)
        self.editors["look_editor"] = self.look_editor.look_editor_frame
        self.look_editor.look_editor_frame.pack()

    def add_variant_editor(self, root):
        self.variant_editor = VariantEditorView(root, self.context)
        self.editors["variant_editor"] = self.variant_editor.variant_editor_frame

    def toggle_editors(self, editor_name:str):
        for editor in self.editors.values():
            editor.pack_forget()

        if editor_name in self.editors:
            self.editors[editor_name].pack(fill="both", expand=True)
        else:
            self.context.services.status.status_update(f"Editor with name: '{editor_name}' not found")

    def sta_thread(self, callback:Callable):
        # time.sleep(2)
        self.dispatcher.begin_invoke(callback)