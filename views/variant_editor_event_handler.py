from tkinter import ttk
from typing import List
from application.sub_variants import SubVariants
from application.switches import Switches
from application.tristate import Tristate
from application.variant import Variant
from application.variants import Variants
from view_models.application_context import ApplicationContext
import tkinter as tk


class VariantEditorEventHandler:
    def __init__(self, context:ApplicationContext):
        self.context = context
        self.context.view_variant_editor_event_handler = self
        self.view = context.view_variant_editor
        self.view_model = context.vm_variant_editor

    def clear_variant_container_widgets(self):
        for widget in self.view.variants_container.winfo_children():
            widget.destroy()

    def on_variant_selected(self, variant:'Variant'):
        if not variant:
            return
        self.view_model.activate_variant(variant) 
        self.view.bind_variant_name_var()
        

    def update_variant_container(self, variants:'Variants'):
        self.clear_variant_container_widgets()

        self.view.variants_container.columnconfigure(0, weight=1)
        frame = ttk.Frame(self.view.variants_container, style="Standard.TFrame")
        frame.grid(row=1, column=0, sticky="nsew", padx=(6, 3))

        # Define column headers
        headers = [("#", 25), ("Variant Set", 200), ("Current Variant", 88)]
        for col_idx, (header, width) in enumerate(headers):
            label = ttk.Label(frame, text=header, anchor="center", relief="raised")
            label.grid(row=0, column=col_idx, sticky="nsew", padx=1, pady=1)

            frame.grid_columnconfigure(col_idx, minsize=width)

        # Configure column weights
        frame.columnconfigure(0, weight=0)  # Adjust column weights as needed
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=0)

        self.grid_rows = []  # To store the row widgets for dynamic updates

        # Populate grid rows
        for row_idx, variant in enumerate(variants, start=1):
            # Row ID (label)
            id_label = ttk.Label(frame, text=str(variant.id), anchor="center") #, relief="sunken")
            id_label.grid(row=row_idx, column=0, sticky="nsew", padx=1, pady=1)
            id_label.bind("<Button-1>", lambda e, var=variant: self.on_variant_selected(var))


            # Name (entry)
            variant_set = ttk.Entry(frame, textvariable=variant.name_var)
            variant_set.grid(row=row_idx, column=1, sticky="nsew", padx=1, pady=1)
            variant_set.bind("<Button-1>", lambda e, var=variant: self.on_variant_selected(var))


            # Look (combobox)
            active_state = ttk.Combobox(frame, values=self.view_model.get_active_state(), textvariable=variant.active_state_var, width=11)  # column / 8
            active_state.grid(row=row_idx, column=2, sticky="nsew", padx=1, pady=1)
            active_state.bind("<Button-1>", lambda e, var=variant: self.on_variant_selected(var))

            # Store row widgets for future updates
            self.grid_rows.append((id_label, variant_set, active_state))

        # Configure row weights
        for row_idx in range(len(variants) + 1):  # +1 for header row
            frame.rowconfigure(row_idx, weight=1)

        if len(variants):
            if not self.view_model.selected_variant:
                self.view_model.selected_variant = variants[-1]

            self.update_sub_variant_container(self.view_model.selected_variant.sub_variants)


    def populate_sub_variants(self, sub_variants:'SubVariants'):
        pass   


    def clear_sub_variant_container_widgets(self):
        for widget in self.view.sub_variants_container.winfo_children():
            widget.destroy()

        # for row in range(self.view.sub_variants_container.grid_size()[1]):
        #     self.view.sub_variants_container.grid_rowconfigure(row, minsize=0)

    def on_sub_variant_selected(self, variant:'Variant'):
        self.context.application.status_message = "Not implemented"
        # if not variant:
        #     return
        # self.view_model.activate_variant(variant)
        # self.populate_sub_variants(variant.sub_variants)        
        # self.view.bind_variant_name_var()
    
    def on_option_selected(self, selected_option:str):
        print(self.__class__.__name__, selected_option)
        # shared_option_var = self.context.vm_variant_editor.get_editing_state_var()
        # if not shared_option_var:
        #     self.context.application.status_message = "activate variant first"
        #     return 
        
        # print("val", shared_option_var.get())



    def on_text_click(self, option):
        print(f"Selected: {option} (state unchanged)")

    def _add_options(self, frame: ttk.Frame, sub_variants:'SubVariants'):
        def on_enter(event, frame:ttk.Frame):
            self.context.application.status_message = "on enter"
            frame.configure(style="Hover.Option.TFrame")

        def on_leave(event, frame:ttk.Frame):
            self.context.application.status_message = "on leave"
            frame.configure(style="Option.TFrame")

        def on_click(event, frame:ttk.Frame, all_frames:List[ttk.Frame]):
            for f in all_frames:
                f.configure(style="Option.TFrame")  # Reset all frames to default style
            frame.configure(style="Selected.Option.TFrame")  # Apply selected style

        options_frame = ttk.Frame(frame, style="Standard.TFrame")
        options_frame.grid(row=0, column=0, sticky="nsew")
        options_frame.rowconfigure(0, weight=1)
        options_frame.columnconfigure(0, weight=1)


        # shared_option = self.context.vm_variant_editor.get_editing_state_var()
        shared_option = self.context.vm_variant_editor.get_active_state_var()
        # shared_option:tk.StringVar = None
        # shared_option = sub_variants.parent.active_state_var if sub_variants else None
        options = Tristate.to_list()
        # if not shared_option:
        #     print(self.__class__.__name__, "options", "shared option still none")
        # else:
        #     print(self.__class__.__name__, "options", shared_option.get())

        containers = []
        for option in options:
            # Create a container frame for each option
            container = ttk.Frame(options_frame, style="Option.TFrame")
            container.grid(sticky="ew", padx=0, pady=0)
            container.columnconfigure(1, weight=1)  # Make the label stretch
            containers.append(container)

            # Add the radiobutton
            rb = ttk.Radiobutton(
                container,
                text="",
                value=option,
                variable=shared_option,
                style="Standard.TRadiobutton",
                command=lambda opt=option: self.on_option_selected(opt)
            )
            rb.grid(row=0, column=0, padx=0)  # Circle only

            # Add the text as a separate label inside the container
            label = ttk.Label(container, text=option, anchor="w", style="Standard.TLabel")
            label.grid(row=0, column=1, sticky="ew", padx=1)

            # Bind clicks on the container
            container.bind("<Enter>", lambda e, f=container: on_enter(e, f))
            container.bind("<Leave>", lambda e, f=container: on_leave(e, f))
            container.bind("<Button-1>", lambda e, f=container, all_f=containers: on_click(e, f, all_f))
            # container.bind("<Button-1>", lambda e, opt=option: self.on_text_click(opt))
            label.bind("<Button-1>", lambda e, opt=option: self.on_text_click(opt))

    def update_sub_variant_container(self, sub_variants:'SubVariants'):
        self.clear_sub_variant_container_widgets()

        outer_frame = ttk.Frame(self.view.sub_variants_container, style="Standard.TFrame")
        outer_frame.grid(row=0, column=0, sticky="nsew", padx=(3, 6))
        outer_frame.columnconfigure(0, weight=1)
        outer_frame.rowconfigure(0, weight=0)
        outer_frame.rowconfigure(1, weight=1)

        self._add_options(outer_frame, sub_variants)

        frame = ttk.Frame(outer_frame, style="Standard.TFrame")
        frame.grid(row=1, column=0, sticky="nsew")


        # Define column headers
        headers = [("#", 25), ("Type", 160), ("Actor", 120), ("Value", 120)]
        for col_idx, (header, width) in enumerate(headers):
            label = ttk.Label(frame, text=header, anchor="center", relief="raised")
            label.grid(row=0, column=col_idx, sticky="nsew", padx=0, pady=0)

            frame.grid_columnconfigure(col_idx, minsize=width)

        frame.columnconfigure(0, weight=0)  # Adjust column weights as needed
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=0)
        frame.columnconfigure(3, weight=0)
        frame.rowconfigure(0, weight=0)
        
        self.grid_rows = []  # To store the row widgets for dynamic updates
        if not sub_variants:
            return
        
        sv = sub_variants.parent.active_sub_variant
        if not sv:
            return
        
        # Populate grid rows
        for row_idx, sub_variant in enumerate(sv.switches, start=1):
            # Row ID (label)
            id_label = ttk.Label(frame, text=str(sub_variant.id), anchor="center") #, relief="sunken")
            id_label.grid(row=row_idx, column=0, sticky="nsew", padx=1, pady=1)
            id_label.bind("<Button-1>", lambda e, var=sub_variant: self.on_sub_variant_selected(var))


            # Name (entry)
            sub_type = ttk.Entry(frame, textvariable=sub_variant.name_var)
            sub_type.grid(row=row_idx, column=1, sticky="nsew", padx=1, pady=1)
            sub_type.bind("<Button-1>", lambda e, var=sub_variant: self.on_sub_variant_selected(var))


            # Look (combobox)
            sub_actor = ttk.Combobox(frame, values=self.view_model.get_active_state(), textvariable=sub_variant.active_state_var, width=15)  # column / 8
            sub_actor.grid(row=row_idx, column=2, sticky="nsew", padx=1, pady=1)
            sub_actor.bind("<Button-1>", lambda e, var=sub_variant: self.on_sub_variant_selected(var))

            sub_value = ttk.Combobox(frame, values=self.view_model.get_active_state(), textvariable=sub_variant.active_state_var, width=15)  # column / 8
            sub_value.grid(row=row_idx, column=2, sticky="nsew", padx=1, pady=1)
            sub_value.bind("<Button-1>", lambda e, var=sub_variant: self.on_sub_variant_selected(var))

            # Store row widgets for future updates
            self.grid_rows.append((id_label, sub_type, sub_actor, sub_value))

        # Configure row weights
        frame.rowconfigure(0, weight=0)  # Header row should not stretch
        for row_idx in range(1, len(sub_variants) + 1):  # Data rows start from 1
            frame.rowconfigure(row_idx, weight=1)  # Allow data rows to stretch

        if len(sub_variants):
            if not self.view_model.selected_variant:
                self.view_model.selected_variant = sub_variants[-1]

        frame.update_idletasks()