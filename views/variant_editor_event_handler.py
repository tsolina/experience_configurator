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

    def clear_container_widgets(self, container:ttk.Frame):
        for widget in container.winfo_children():
            grid_info = widget.grid_info()

            if grid_info.get('row') != 0:
                widget.destroy()

    def clear_variant_container_widgets(self):
        self.clear_container_widgets(self.view.variant_frame)
        # for widget in self.view.variants_container.winfo_children():
        #     widget.destroy()

    def clear_sub_variant_container_widgets(self):
        for widget in self.view.sub_variants_container.winfo_children():
            widget.destroy()

    # switch_container

    def on_variant_selected(self, variant:'Variant'):
        if not variant:
            return
        self.view_model.activate_variant(variant) 
        self.view.bind_variant_name_var()
        self.update_sub_variant_container()
        

    def update_variant_container(self):#, variants:'Variants'):
        self.clear_variant_container_widgets()

        variants = self.view_model.get_variants()
        if variants is None:
            return
        
        # self.clear_variant_container_widgets()

        frame = self.view.variant_frame
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
            if not hasattr(variant, "active_state_var"):
                variant.active_state_var = tk.StringVar(value=variant.active_state)
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
        print(__name__, "not implemented") 




    def on_switch_selected(self, switch:'Switch'):
        self.view_model.activate_switch(switch)
        # self.populate_sub_variants(variant.sub_variants)        
        # self.view.bind_variant_name_var()
    

    def update_options(self):
        # Get the shared_option variable
        shared_option = self.context.vm_variant_editor.get_active_state_var()
        if shared_option is None:
            return

        # Update the binding for each option widget
        for option, widgets in self.view.option_widgets.items():
            # Update the variable binding for the radiobutton
            rb: ttk.Radiobutton = widgets["radiobutton"]
            rb.configure(variable=shared_option)

            # Update the variable value (if needed)
            if shared_option.get() == option:
                shared_option.set(option)

            # Update the label style dynamically
            label: ttk.Label = widgets["label"]
            style = self.view_model.get_sub_variant_label_style(option)
            label.configure(style=style)



    def clear_switches_container_widgets(self):
        for widget in self.view.switch_container.winfo_children():
            grid_info = widget.grid_info()

            if grid_info.get('row') != 0:
                widget.destroy()

    def update_switches_container(self):#, switches:'Switches'):
        self.clear_switches_container_widgets()
        switches = self.view_model.get_editing_switches()
        if not switches:
            return
        
        self.context.application.status_message = f"updating switches {len(switches)}"

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

    def update_sub_variant_container(self): #, sub_variants:'SubVariants'):
        self.update_options()
        self.update_switches_container()
        self.view_model.ensure_active_sub_variant()
        