from typing import TYPE_CHECKING
import tkinter as tk
from tkinter import ttk

from application.observable_list import ObservableList
from application.variant import Variant
from view_models.application_context import ApplicationContext
from view_models.variant_editor_view_model import VariantEditorViewModel
from views.variant_editor_event_handler import VariantEditorEventHandler

if TYPE_CHECKING:
    from views.main_window_view import MainWindowView

class VariantEditorView():
    def __init__(self, root, context:ApplicationContext):
        self.context = context
        self.context.view_variant_editor = self
        self.view_model = context.vm_variant_editor

        self.event_handler = VariantEditorEventHandler(context)

        self.add_main_frame(root)
        self.add_title()
        self.add_data_grid()
        self.add_look_controls(root)

        self.add_active_variant()
        self.add_variant_grid()
        self.add_variant_controls(root)

    def update_variant(self, variants:ObservableList['Variant']):
        pass

    def add_main_frame(self, root):
        self.variant_editor_frame = tk.Frame(root, background=root['bg'])
        self.variant_editor_frame.grid_rowconfigure(0, weight=0)  # Header row (fixed)
        self.variant_editor_frame.grid_rowconfigure(1, weight=1)  # Content row (expands)
        self.variant_editor_frame.grid_rowconfigure(2, weight=0)  # Footer row (fixed)
        self.variant_editor_frame.grid_columnconfigure(0, weight=1)
        self.variant_editor_frame.grid_columnconfigure(1, weight=1)

    def add_title(self):
        title = ttk.Label(self.variant_editor_frame, text="Variant editor", style="Red.TLabel")
        title.grid(row=0, column=0, sticky='w')

    def add_data_grid(self):
        self.variants_container = ttk.Frame(self.variant_editor_frame, style="Standard.TFrame")
        self.variants_container.grid(row=1, column=0, sticky="nsew")

        # Sample data rows from view model
        variants = self.view_model.get_variants()
        self.event_handler.update_variant_container(variants)
        return
    
    def bind_variant_name_var(self):
        name_var = self.view_model.get_active_variant_var()
        if name_var:
            self.variant_name.config(textvariable=name_var)
        else:
            self.variant_name.config(text="select variant")


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
        outer_frame = tk.Frame(self.variant_editor_frame, background=root['bg'], height=30)
        outer_frame.grid(row=2, column=0, sticky="w", padx=4, pady=3)
        outer_frame.grid_propagate(False)

        button_frame = tk.Frame(outer_frame, background=root['bg'])
        button_frame.pack(side="left", fill="both")

        self.create_button(button_frame, "New Variant", "create new variant", self.view_model.new_variant)
        self.create_button(button_frame, "Clone", "clone selected variant", self.view_model.clone_variant)
        self.create_button(button_frame, "Delete", "delete selected variant", self.view_model.delete_variant)

    def add_active_variant(self):
        container = ttk.Frame(self.variant_editor_frame, style='Standard.TFrame')
        container.grid(row=0, column=1, sticky='w')

        title = ttk.Label(container, text="Active variant:", style="Red.TLabel")
        title.pack(side="left", anchor="w")

        self.variant_name = ttk.Label(container, style="Standard.TLabel")
        self.variant_name.pack(side="left", anchor="w")
        self.bind_variant_name_var()

    def add_variant_grid(self):
        self.sub_variants_container = ttk.Frame(self.variant_editor_frame, style="Standard.TFrame")
        self.sub_variants_container.grid(row=1, column=1, sticky="nsew")
        self.sub_variants_container.columnconfigure(0, weight=1)
        self.sub_variants_container.rowconfigure(0, weight=1)

        # Sample data rows from view model
        sub_variants = self.view_model.get_sub_variants()
        self.switch_container:ttk.Frame = None
        self.event_handler.update_sub_variant_container(sub_variants)
        return

    def add_variant_controls(self, root):
        outer_frame = tk.Frame(self.variant_editor_frame, background=root['bg'], height=30)
        outer_frame.grid(row=2, column=1, sticky="w", padx=4, pady=3)
        outer_frame.grid_propagate(False)

        button_frame = tk.Frame(outer_frame, background=root['bg'])
        button_frame.pack(side="left", fill="both")

        self.create_button(button_frame, "New Visibility", "Create new visibility switch", self.view_model.create_new_visibility_switch)
        self.create_button(button_frame, "New Look", "Create new look switch", self.not_implemented)
        self.create_button(button_frame, "New Code State", "Create new Code State switch", self.not_implemented)
        self.create_button(button_frame, "Delete", "delete selected switch", self.not_implemented)

    def not_implemented(self):
        self.context.application.status_message = "Not implemented yet"