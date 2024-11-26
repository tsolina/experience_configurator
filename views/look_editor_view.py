from typing import TYPE_CHECKING
import tkinter as tk
from tkinter import ttk

from application.configuration import Configuration
from application.observable_list import ObservableList
from application.project import Project
from application.tristate import Tristate
from view_models.application_context import ApplicationContext
from view_models.look_editor_view_model import LookEditorViewModel
from views.look_editor_event_handler import LookEditorEventHandler
import application.widgets as widgets

if TYPE_CHECKING:
    from views.main_window_view import MainWindowView

class LookEditorView():
    # def __init__(self, root, parent:'MainWindowView', view_model: 'LookEditorViewModel'):
    def __init__(self, root, context:ApplicationContext):
        # print(self.__class__.__name__, "init")
        self.context = context
        self.context.view_look_editor = self
        self.view_model = self.context.vm_look_editor
        self.event_handler = LookEditorEventHandler(context)

        self.add_main_frame(root)
        self.add_title()
        self.add_data_grid()
        self.add_look_controls(root)

        self.add_active_configuration()
        self.add_configuration_grid()
        self.add_configuration_controls(root)


    def add_main_frame(self, root):
        self.look_editor_frame = tk.Frame(root, background=root['bg'])
        self.look_editor_frame.pack(fill='both', expand=True)
        self.look_editor_frame.grid_rowconfigure(0, weight=0)  # Header row (fixed)
        self.look_editor_frame.grid_rowconfigure(1, weight=1)  # Content row (expands)
        self.look_editor_frame.grid_rowconfigure(2, weight=0)  # Footer row (fixed)
        self.look_editor_frame.grid_columnconfigure(0, weight=1)
        self.look_editor_frame.grid_columnconfigure(1, weight=1)

    def bind_config_name_var(self):
        name_var = self.view_model.get_active_config_var()
        # print(self.__class__.__name__, "bind_config_name_var", name_var)
        if name_var:
            self.config_name.config(textvariable=name_var)
        else:
            self.config_name.config(text="select configuration")


    def add_title(self):
        container = ttk.Frame(self.look_editor_frame)
        container.grid(row=0, column=0, sticky='w')

        title = ttk.Label(container, text="Look editor", style="Red.TLabel")
        title.pack(side="left", anchor="w")

    def add_data_grid(self):
        self.configurations_container = ttk.Frame(self.look_editor_frame, style="Standard.TFrame")
        self.configurations_container.grid(row=1, column=0, sticky="nsew")

        # Sample data rows from view model
        # self.context.vm_main_window.activate_project()
        configurations = self.view_model.get_configurations()
        self.event_handler.update_treeview(configurations)
        return

    def add_tooltip(self, widget: tk.Widget, text: str):
        def on_enter(event):
            self.context.vm_main_window.status_update(text)

        def on_leave(event):
            self.context.vm_main_window.status_reset()

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)


    def create_button(self, parent, text, tooltip, command):
        # Button with padding to resemble a border
        button = ttk.Button(parent, text=text, command=command)
        button.pack(side="left", padx=5, pady=2)
        
        # Bind tooltip events
        self.add_tooltip(button, tooltip)

    def add_look_controls(self, root):
        outer_frame = tk.Frame(self.look_editor_frame, background=root['bg'], height=30)
        outer_frame.grid(row=2, column=0, sticky="w", padx=4, pady=3)
        outer_frame.grid_propagate(False)

        button_frame = tk.Frame(outer_frame, background=root['bg'])
        button_frame.pack(side="left", fill="both")

        self.create_button(button_frame, "New configuration", "create new look configuration", self.view_model.new_configuration)
        self.create_button(button_frame, "Clone", "clone selected configuration", self.view_model.clone_configuration)
        self.create_button(button_frame, "Delete", "delete selected configuration", self.view_model.delete_configuration)

    def add_active_configuration(self):
        container = ttk.Frame(self.look_editor_frame, style="Standard.TFrame")
        container.grid(row=0, column=1, sticky='w')

        title = ttk.Label(container, text="Active configuration:", style="Red.TLabel")
        title.pack(side="left", anchor="w")

        self.config_name = ttk.Label(container, style="Standard.TLabel")
        self.config_name.pack(side="left", anchor="w")
        self.bind_config_name_var()

    def add_configuration_grid(self):
        frame = ttk.Frame(self.look_editor_frame)
        frame.grid(row=1, column=1, sticky="nsew")

        # Define columns
        columns = ("id", "actor", "type", "error")
        self.actors_tree = ttk.Treeview(frame, columns=columns, show="headings")
        
        # Set column headers
        self.actors_tree.heading("id", text="#")
        self.actors_tree.heading("actor", text="Actor")
        self.actors_tree.heading("type", text="Type")
        self.actors_tree.heading("error", text="Error")

        # Set column widths
        self.actors_tree.column("id", width=10, anchor="center")
        self.actors_tree.column("actor", minwidth=100, width=180)
        self.actors_tree.column("type", minwidth=40, width=50)
        self.actors_tree.column("error", width=50, anchor="center")

        self.actors_tree.pack(fill="both", expand=True)

        # Add a callback for selection change
        self.actors_tree.bind("<<TreeviewSelect>>", self.event_handler.on_actors_selection_change)

    def add_configuration_controls(self, root):
        outer_frame = tk.Frame(self.look_editor_frame, background=root['bg'], height=30)
        outer_frame.grid(row=2, column=1, sticky="w", padx=4, pady=3)
        outer_frame.grid_propagate(False)

        button_frame = tk.Frame(outer_frame, background=root['bg'])
        button_frame.pack(side="left", fill="both")

        self.create_button(button_frame, "Select", "select actors from catia selection", self.event_handler.btn_select_actors)
        self.create_button(button_frame, "Deselect", "remove selected actor from list", self.event_handler.btn_deselect_actors)
        self.create_button(button_frame, "Delete", "delete selected actor", self.event_handler.btn_delete_actor)
