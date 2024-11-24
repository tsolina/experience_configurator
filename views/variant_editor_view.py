from typing import TYPE_CHECKING
import tkinter as tk
from tkinter import ttk

from application.observable_list import ObservableList
from application.variant import Variant
from view_models.application_context import ApplicationContext
from view_models.variant_editor_view_model import VariantEditorViewModel

if TYPE_CHECKING:
    from views.main_window_view import MainWindowView

class VariantEditorView():
    # def __init__(self, root, parent:'MainWindowView', view_model: 'VariantEditorViewModel'):
    def __init__(self, root, context:ApplicationContext):
        self.context = context
        self.context.view_variant_editor = self
        # self.main_window_view = parent
        self.view_model = context.vm_variant_editor
        # self.view_model.root_model = parent.view_model

        self.add_main_frame(root)
        self.add_title()
        self.add_data_grid()
        self.add_look_controls(root)

        self.add_active_configuration()
        self.add_configuration_grid()
        self.add_configuration_controls(root)

        # self.variant_editor_frame.pack_forget()

    def update_variant(self, variants:ObservableList['Variant']):
        pass

    def add_main_frame(self, root):
        self.variant_editor_frame = tk.Frame(root, background=root['bg'])
        # self.variant_editor_frame.pack(fill='both', expand=True)
        # self.variant_editor_frame.grid(row=1, column=0, sticky='nsew')
        self.variant_editor_frame.grid_rowconfigure(0, weight=0)  # Header row (fixed)
        self.variant_editor_frame.grid_rowconfigure(1, weight=1)  # Content row (expands)
        self.variant_editor_frame.grid_rowconfigure(2, weight=0)  # Footer row (fixed)
        self.variant_editor_frame.grid_columnconfigure(0, weight=1)
        self.variant_editor_frame.grid_columnconfigure(1, weight=1)

    def add_title(self):
        title = ttk.Label(self.variant_editor_frame, text="Variant editor", style="Red.TLabel")
        title.grid(row=0, column=0, sticky='w')

    def add_data_grid(self):
        frame = ttk.Frame(self.variant_editor_frame)
        frame.grid(row=1, column=0, sticky="nsew")

        # Define columns
        columns = ("id", "variant_set", "current_variant")
        self.variant_editor_tree = ttk.Treeview(frame, columns=columns, show="headings")
        
        # Set column headers
        self.variant_editor_tree.heading("id", text="#")
        self.variant_editor_tree.heading("variant_set", text="Variant Set")
        self.variant_editor_tree.heading("current_variant", text="Current Variant")

        # Set column widths
        self.variant_editor_tree.column("id", width=10, anchor="center")
        self.variant_editor_tree.column("variant_set", minwidth=80, width=100)
        self.variant_editor_tree.column("current_variant", minwidth=175, width=175)

        # Insert sample data
        for i in range(10):  # Sample data rows
            self.variant_editor_tree.insert("", "end", values=(i+1, f"Item {i+1}", ""))

        self.variant_editor_tree.pack(fill="both", expand=True)

        # Add a callback for selection change
        self.variant_editor_tree.bind("<<TreeviewSelect>>", self.on_selection_change)

    def on_selection_change(self, event):
        # Handle selection change
        selected_item = self.variant_editor_tree.selection()
        print("Selection changed:", selected_item)

    def add_tooltip(self, widget: tk.Widget, text: str):
        def on_enter(event):
            self.main_window_view.view_model.status_update(text)

        def on_leave(event):
            self.main_window_view.view_model.status_reset()

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)


    def create_button(self, parent, text, tooltip, command):
        # Button with padding to resemble a border
        button = ttk.Button(parent, text=text, command=command)
        button.pack(side="left", padx=5, pady=2)
        
        # Bind tooltip events
        self.add_tooltip(button, tooltip)

    def add_look_controls(self, root):
        outer_frame = tk.Frame(self.variant_editor_frame, background=root['bg'], height=30)
        outer_frame.grid(row=2, column=0, sticky="w", padx=4, pady=3)
        outer_frame.grid_propagate(False)

        button_frame = tk.Frame(outer_frame, background=root['bg'])
        button_frame.pack(side="left", fill="both")

        self.create_button(button_frame, "New Variant", "create new variant", self.new_configuration)
        self.create_button(button_frame, "Clone", "clone selected variant", self.clone_configuration)
        self.create_button(button_frame, "Delete", "delete selected variant", self.delete_configuration)
  
    def new_configuration(self):
        print("New configuration clicked")

    def clone_configuration(self):
        print("Clone clicked")

    def delete_configuration(self):
        print("Delete clicked")

    def add_active_configuration(self):
        title = ttk.Label(self.variant_editor_frame, text="Active variant:", style="Red.TLabel")
        title.grid(row=0, column=1, sticky='w')

    def add_configuration_grid(self):
        frame = ttk.Frame(self.variant_editor_frame)
        frame.grid(row=1, column=1, sticky="nsew")

        # Define columns
        columns = ("id", "type", "actor", "value")
        self.active_variant_tree = ttk.Treeview(frame, columns=columns, show="headings")
        
        # Set column headers
        self.active_variant_tree.heading("id", text="#")
        self.active_variant_tree.heading("type", text="Actor")
        self.active_variant_tree.heading("actor", text="Type")
        self.active_variant_tree.heading("value", text="Error")

        # Set column widths
        self.active_variant_tree.column("id", width=10, anchor="center")
        self.active_variant_tree.column("type", minwidth=100, width=180)
        self.active_variant_tree.column("actor", minwidth=40, width=50)
        self.active_variant_tree.column("value", width=50, anchor="center")

        # Insert sample data
        for i in range(10):  # Sample data rows
            self.active_variant_tree.insert("", "end", values=(i+1, f"Item {i+1}", "", "", ""))

        self.active_variant_tree.pack(fill="both", expand=True)

        # Add a callback for selection change
        self.active_variant_tree.bind("<<TreeviewSelect>>", self.on_selection_change)

    def add_configuration_controls(self, root):
        outer_frame = tk.Frame(self.variant_editor_frame, background=root['bg'], height=30)
        outer_frame.grid(row=2, column=1, sticky="w", padx=4, pady=3)
        outer_frame.grid_propagate(False)

        button_frame = tk.Frame(outer_frame, background=root['bg'])
        button_frame.pack(side="left", fill="both")

        self.create_button(button_frame, "New Visibility", "Create new visibility switch", self.new_configuration)
        self.create_button(button_frame, "New Look", "Create new look switch", self.clone_configuration)
        self.create_button(button_frame, "New Code State", "Create new Code State switch", self.delete_configuration)
        self.create_button(button_frame, "Delete", "delete selected switch", self.delete_configuration)