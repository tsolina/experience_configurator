from tkinter import ttk
from typing import List
from application.actors import Actors
from application.sub_variants import SubVariants
from application.switch import Switch
from application.switches import Switches
from application.tristate import Tristate
from application.variant import Variant
from application.variant_type import VariantType
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

        self.view_model.ensure_active_variant()


    def populate_sub_variants(self, sub_variants:'SubVariants'):
        pass   


    def clear_sub_variant_container_widgets(self):
        for widget in self.view.sub_variants_container.winfo_children():
            widget.destroy()

    def on_switch_selected(self, switch:'Switch'):
        self.view_model.activate_switch(switch)
        # self.populate_sub_variants(variant.sub_variants)        
        # self.view.bind_variant_name_var()
    
    def on_option_selected(self, selected_option:str):
        self.view_model.on_sub_variant_selected(selected_option)
        # print(self.__class__.__name__, "on_option_selected", selected_option)
        # shared_option_var = self.context.vm_variant_editor.get_editing_state_var()
        # if not shared_option_var:
        #     self.context.application.status_message = "activate variant first"
        #     return 
        
        # print("val", shared_option_var.get())



    def _add_options(self, frame: ttk.Frame):
        def on_enter(event, widget:ttk.Label):
            if not self.view_model.is_editing_sub_variant(widget.cget("text")):
                widget.configure(style="Hover.Option.TLabel")
                self.context.application.status_message = "on enter"

        def on_leave(event, widget:ttk.Label):
            if not self.view_model.is_editing_sub_variant(widget.cget("text")):
                widget.configure(style="Option.TLabel")
                self.context.application.status_message = "on leave"

        def on_click(event, widget:ttk.Label, all_widgets:List[ttk.Label], option:str):
            for w in all_widgets:
                w.configure(style="Option.TLabel")
            widget.configure(style="Selected.Option.TLabel")
            self.view_model.activate_editing_sub_variant(option)

        options_frame = ttk.Frame(frame, style="Standard.TFrame")
        options_frame.grid(row=0, column=0, sticky="nsew")
        options_frame.rowconfigure(0, weight=1)
        options_frame.columnconfigure(0, weight=1)

        shared_option = self.context.vm_variant_editor.get_active_state_var()
        options = Tristate.to_list()

        widgets = []
        for option in options:
            # Create a container frame for each option
            container = ttk.Frame(options_frame, style="Option.TFrame")
            container.grid(sticky="ew", padx=0, pady=0)
            container.columnconfigure(1, weight=1)  # Make the label stretch

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

            label = ttk.Label(container, text=option, anchor="w", style=self.view_model.get_sub_variant_label_style(option))
            label.grid(row=0, column=1, sticky="ew", padx=1, pady=0)
            widgets.append(label)

            # Bind clicks on the label
            label.bind("<Enter>", lambda e, f=label: on_enter(e, f))
            label.bind("<Leave>", lambda e, f=label: on_leave(e, f))
            label.bind("<Button-1>", lambda e, f=label, all_f=widgets, opt=option: on_click(e, f, all_f, opt))

    def update_sub_variant_container(self): #, sub_variants:'SubVariants'):
        self.clear_sub_variant_container_widgets()

        outer_frame = ttk.Frame(self.view.sub_variants_container, style="Standard.TFrame")
        outer_frame.grid(row=0, column=0, sticky="nsew", padx=(3, 6))
        outer_frame.columnconfigure(0, weight=1)
        outer_frame.rowconfigure(0, weight=0)
        outer_frame.rowconfigure(1, weight=1)

        self._add_options(outer_frame)

        frame = ttk.Frame(outer_frame, style="Standard.TFrame")
        frame.grid(row=1, column=0, sticky="nsew")

        # Define column headers
        headers = [("#", 25), ("Type", 120), ("Actor", 160), ("Value", 120)]
        for col_idx, (header, width) in enumerate(headers):
            label = ttk.Label(frame, text=header, anchor="center", relief="raised")
            label.grid(row=0, column=col_idx, sticky="nsew", padx=0, pady=2)

            frame.grid_columnconfigure(col_idx, minsize=width)

        frame.columnconfigure(0, weight=0)  # Adjust column weights as needed
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=2)
        frame.columnconfigure(3, weight=1)
        frame.rowconfigure(0, weight=0)
        self.view.switch_container = frame
        
        self.update_switches_container()
        self.view_model.ensure_active_sub_variant()

        frame.update_idletasks()


    def clear_switches_container_widgets(self):
        for widget in self.view.switch_container.winfo_children():
            grid_info = widget.grid_info()

            if grid_info.get('row') != 0:
                widget.destroy()

    def update_switches_container(self):#, switches:'Switches'):
        switches = self.view_model.get_editing_switches()
        if not switches:
            return
        
        self.context.application.status_message = f"updating switches {len(switches)}"
        self.clear_switches_container_widgets()

        self.grid_rows = []  # To store the row widgets for dynamic updates

        # Populate grid rows
        for row_idx, switch in enumerate(switches, start=1):
            # print(switch.name, switch.id)
            # Row ID (label)
            id_label = ttk.Label(self.view.switch_container, text=str(switch.id), anchor="center") #, relief="sunken")
            id_label.grid(row=row_idx, column=0, sticky="nsew", padx=1, pady=1)
            id_label.bind("<Button-1>", lambda e, var=switch: self.on_switch_selected(var))


            # Name (entry)
            sub_type = ttk.Label(self.view.switch_container, textvariable=switch.type_var)
            sub_type.grid(row=row_idx, column=1, sticky="nsew", padx=1, pady=1)
            sub_type.bind("<Button-1>", lambda e, var=switch: self.on_switch_selected(var))


            if switch.type_ == VariantType.Visibility:
                sub_actor = ttk.Label(self.view.switch_container, textvariable=switch.name_var, width=20)#, anchor="center") #, relief="sunken")
            elif switch.type_ == VariantType.Look:
                sub_actor = ttk.Combobox(self.view.switch_container, values=switch.actor_collection, textvariable=switch.name_var, width=20)            
            else:
            # Look (combobox)
                sub_actor = ttk.Combobox(self.view.switch_container, values=switch.get_list_of_variants(), textvariable=switch.name_var, width=20)  # column / 8
            sub_actor.grid(row=row_idx, column=2, sticky="nsew", padx=1, pady=1)
            sub_actor.bind("<Button-1>", lambda e, var=switch: self.on_switch_selected(var))

            if switch.type_ == VariantType.Look:
                sub_value = ttk.Combobox(self.view.switch_container, values=switch.values_collection, textvariable=switch.active_value_var, width=15)
            else:
                sub_value = ttk.Combobox(self.view.switch_container, values=self.view_model.get_active_state(), textvariable=switch.active_value_var, width=15)  # column / 8
            sub_value.grid(row=row_idx, column=3, sticky="nsew", padx=1, pady=1)
            sub_value.bind("<Button-1>", lambda e, var=switch: self.on_switch_selected(var))

            # Store row widgets for future updates
            self.grid_rows.append((id_label, sub_type, sub_actor, sub_value))

        self.view_model.ensure_editing_switches()
        