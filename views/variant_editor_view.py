from typing import TYPE_CHECKING, List
import tkinter as tk
from tkinter import ttk

from application.observable_list import ObservableList
from application.tristate import Tristate
from application.variant import Variant
from services.logging_service import LoggingService
from view_models.application_context import ApplicationContext
from view_models.variant_editor_view_model import VariantEditorViewModel
from views.grid_manager import GridManager
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
        self.variants_grid_manager:GridManager = None
        self.add_data_grid()
        self.add_look_controls(root)

        self.add_active_variant()
        
        self.sub_variants_grid_manager:GridManager = None
        self.create_sub_variant_grid()
        # self.add_variant_grid()
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

        self.variants_container.columnconfigure(0, weight=1)
        frame = ttk.Frame(self.variants_container, style="Standard.TFrame")
        frame.grid(row=1, column=0, sticky="nsew", padx=(6, 3))
        self.variant_frame = frame

        # Label, Entry, Combobox
        variants_headers = [
            ("#", 25, ttk.Label), ("Variant Set", 200, ttk.Entry), ("Current Variant", 88, ttk.Combobox)
        ]
        self.variants_grid_manager = GridManager(frame, variants_headers)

        # Configure column weights
        frame.columnconfigure(0, weight=0)  # Adjust column weights as needed
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=0)
    
    def bind_variant_name_var(self):
        name_var = self.view_model.get_active_variant_var()
        if name_var:
            self.variant_name.config(textvariable=name_var)
        else:
            self.variant_name.config(text="select variant")


    def add_tooltip(self, widget: tk.Widget, text: str):
        def on_enter(event):
            self.context.services.status.status_update(text)

        def on_leave(event):
            self.context.services.status.status_reset()

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


    def on_option_selected(self, selected_option:str, var:tk.StringVar):
        self.view_model.on_sub_variant_selected(selected_option)

    def _add_options(self, frame: ttk.Frame):
        def on_enter(event, widget:ttk.Label):
            if not self.view_model.is_editing_sub_variant(widget.cget("text")):
                widget.configure(style="Hover.Option.TLabel")
                self.context.services.status.status_update("on enter")

        def on_leave(event, widget:ttk.Label):
            if not self.view_model.is_editing_sub_variant(widget.cget("text")):
                widget.configure(style="Option.TLabel")
                self.context.services.status.status_update("on leave")

        def on_click(event, widget:ttk.Label, all_widgets:List[ttk.Label], option:str):
            for w in all_widgets:
                w.configure(style="Option.TLabel")
            widget.configure(style="Selected.Option.TLabel")
            self.view_model.activate_editing_sub_variant(option)

        shared_option = self.context.vm_variant_editor.get_active_state_var() or tk.StringVar(value="")

        options_frame = ttk.Frame(frame, style="Standard.TFrame")
        options_frame.grid(row=0, column=0, sticky="nsew")
        options_frame.rowconfigure(0, weight=1)
        options_frame.columnconfigure(0, weight=1)

        options = Tristate.to_list()

        widgets = []
        self.option_widgets = {}
        for option in options:
            # Create a container frame for each option
            container = ttk.Frame(options_frame, style="Option.TFrame")
            container.grid(sticky="ew", padx=0, pady=0)
            container.columnconfigure(1, weight=1)  # Make the label stretch

            # Add the radiobutton
            # var = tk.StringVar(value=shared_option.get())
            rb = ttk.Radiobutton(
                container,
                text="",
                value=option,
                variable=shared_option,
                style="Standard.TRadiobutton",
                command=lambda opt=option: self.on_option_selected(opt, shared_option)
            )
            rb.grid(row=0, column=0, padx=0)  # Circle only

            label = ttk.Label(container, text=option, anchor="w", style=self.view_model.get_sub_variant_label_style(option))
            label.grid(row=0, column=1, sticky="ew", padx=1, pady=0)
            widgets.append(label)

            # Bind clicks on the label
            label.bind("<Enter>", lambda e, f=label: on_enter(e, f))
            label.bind("<Leave>", lambda e, f=label: on_leave(e, f))
            label.bind("<Button-1>", lambda e, f=label, all_f=widgets, opt=option: on_click(e, f, all_f, opt))

            self.option_widgets[option] = {
                "radiobutton": rb,
                "label": label,
                "var": shared_option     
            }

    def create_sub_variant_grid(self):
        self.sub_variants_container = ttk.Frame(self.variant_editor_frame, style="Standard.TFrame")
        self.sub_variants_container.grid(row=1, column=1, sticky="nsew")
        self.sub_variants_container.columnconfigure(0, weight=1)
        self.sub_variants_container.rowconfigure(0, weight=1)

        outer_frame = ttk.Frame(self.sub_variants_container, style="Standard.TFrame")
        outer_frame.grid(row=0, column=0, sticky="nsew", padx=(3, 6))
        outer_frame.columnconfigure(0, weight=1)
        outer_frame.rowconfigure(0, weight=0)
        outer_frame.rowconfigure(1, weight=1)

        self._add_options(outer_frame)

        frame = ttk.Frame(outer_frame, style="Standard.TFrame")
        frame.grid(row=1, column=0, sticky="nsew")
        self.switch_container = frame

        # Label, Label, [Label, Combobox], Combobox
        sub_variants_headers = [
            ("#", 25, ttk.Label), ("Type", 120, ttk.Label), ("Actor", 160, [ttk.Label, ttk.Combobox]), ("Value", 120, ttk.Combobox)
        ]
        self.sub_variants_grid_manager = GridManager(frame, sub_variants_headers)

        frame.columnconfigure(0, weight=0)  # Adjust column weights as needed
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=2)
        frame.columnconfigure(3, weight=1)
        frame.rowconfigure(0, weight=0)

    def add_variant_controls(self, root):
        outer_frame = tk.Frame(self.variant_editor_frame, background=root['bg'], height=30)
        outer_frame.grid(row=2, column=1, sticky="w", padx=4, pady=3)
        outer_frame.grid_propagate(False)

        button_frame = tk.Frame(outer_frame, background=root['bg'])
        button_frame.pack(side="left", fill="both")

        self.create_button(button_frame, "New Visibility", "Create new visibility switch", self.view_model.create_new_visibility_switch)
        self.create_button(button_frame, "New Look", "Create new look switch", self.view_model.create_new_look_switch)
        self.create_button(button_frame, "New Code State", "Create new Code State switch", self.view_model.new_code_state_switch)
        self.create_button(button_frame, "Delete", "delete selected switch", self.view_model.delete_switch)

    def not_implemented(self):
        self.context.services.status.status_update("Not implemented yet")