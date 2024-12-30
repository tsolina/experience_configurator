from tkinter import ttk
from typing import List, Tuple
from application.actors import Actors
from application.sub_variants import SubVariants
from application.switch import Switch
from application.switches import Switches
from application.tristate import Tristate
from application.variant import Variant
from application.variant_type import VariantType
from application.variants import Variants
from services.logging_service import LoggingService
from view_models.application_context import ApplicationContext
import tkinter as tk

from views.cell_data import CellData


class VariantEditorEventHandler:
    def __init__(self, context:ApplicationContext):
        self.context = context
        self.context.view_variant_editor_event_handler = self
        self.view = context.view_variant_editor
        self.view_model = context.vm_variant_editor
        self.grid_rows:List[Tuple[ttk.Label, ttk.Label, ttk.Widget, ttk.Combobox]] = [] # To store the row widgets for dynamic updates
        
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
        

    def update_variant_container(self):
        variants = self.view_model.get_variants()
        
        if variants is None:
            self.view.variants_grid_manager.hide_all_rows()
            return

        for row_idx, variant in enumerate(variants, start=1):
            row_widgets = self.view.variants_grid_manager.get_or_add_row(row_idx)

            # ID Label
            id_label = CellData(widgets=row_widgets, 
                                name="id", 
                                row_id=row_idx, 
                                column_id=0, 
                                widget_class=ttk.Label, 
                                options={"text": str(variant.id), "anchor": "center"},
                                bind={"<Button-1>": lambda e, var=variant: self.on_variant_selected(var)})
            self.view.variants_grid_manager.update_cell(id_label)

            # Name
            name_entry = CellData(widgets=row_widgets, 
                                    name="name", 
                                    row_id=row_idx, 
                                    column_id=1, 
                                    widget_class=ttk.Entry, 
                                    options={"textvariable": variant.name_var},
                                    bind={"<Button-1>": lambda e, var=variant: self.on_variant_selected(var)})
            self.view.variants_grid_manager.update_cell(name_entry)

            # Look (combobox)
            if not hasattr(variant, "active_state_var"):
                variant.active_state_var = tk.StringVar(value=variant.active_state)
            value_options = {
                "values": self.view_model.get_active_state(), 
                "textvariable": variant.active_state_var, 
                "width": 11
            }
            sub_value = CellData(widgets=row_widgets, 
                                name="sub_value", 
                                row_id=row_idx, 
                                column_id=2, 
                                widget_class=ttk.Combobox, 
                                options=value_options,
                                bind={"<Button-1>": lambda e, var=variant: self.on_variant_selected(var)}
                                )
            self.view.variants_grid_manager.update_cell(sub_value)

        self.view.variants_grid_manager.hide_extra_rows(len(variants))

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

    def update_switches_container(self):
        switches = self.view_model.get_editing_switches()
        # LoggingService.log_point(self, "switches", switches=switches)
        if not switches:
            self.view.sub_variants_grid_manager.hide_all_rows()  # Hide all rows without clearing them
            return

        self.context.services.status.status_update(f"updating switches {len(switches)}")

        # Prepare row data based on switches
        for row_idx, switch in enumerate(switches, start=1):
            row_widgets = self.view.sub_variants_grid_manager.get_or_add_row(row_idx)

            # ID Label
            id_label = CellData(widgets=row_widgets, 
                                name="id", 
                                row_id=row_idx, 
                                column_id=0, 
                                widget_class=ttk.Label, 
                                options={"text": str(switch.id), "anchor": "center"},
                                bind={"<Button-1>": lambda e, var=switch: self.on_switch_selected(var)})
            self.view.sub_variants_grid_manager.update_cell(id_label)

            # Sub Type Label
            sub_type_label = CellData(widgets=row_widgets, 
                                name="sub_type", 
                                row_id=row_idx, 
                                column_id=1, 
                                widget_class=ttk.Label, 
                                options={"textvariable": switch.type_var},
                                bind={"<Button-1>": lambda e, var=switch: self.on_switch_selected(var)}
                                )
            self.view.sub_variants_grid_manager.update_cell(sub_type_label)

            # Sub Actor (Label or Combobox)
            if switch.type_ == VariantType.Visibility:
                actor_type = ttk.Label
                actor_options = {"textvariable": switch.name_var, "width": 20}
            else:
                actor_type = ttk.Combobox
                actor_values = switch.actor_collection if switch.type_ == VariantType.Look else switch.get_list_of_variants()
                actor_options = {"values": actor_values, "textvariable": switch.name_var, "width": 20}
            sub_actor = CellData(widgets=row_widgets, 
                                name="sub_actor", 
                                row_id=row_idx, 
                                column_id=2, 
                                widget_class=actor_type, 
                                options=actor_options,
                                bind={"<Button-1>": lambda e, var=switch: self.on_switch_selected(var)}
                                )
            self.view.sub_variants_grid_manager.update_cell(sub_actor)


            # Sub Value Combobox
            value_options = {
                "values": switch.values_collection if switch.type_ == VariantType.Look else self.view_model.get_active_state(),
                "textvariable": switch.active_value_var,
                "width": 15
            }
            sub_value = CellData(widgets=row_widgets, 
                                name="sub_value", 
                                row_id=row_idx, 
                                column_id=3, 
                                widget_class=ttk.Combobox, 
                                options=value_options,
                                bind={"<Button-1>": lambda e, var=switch: self.on_switch_selected(var)}
                                )
            self.view.sub_variants_grid_manager.update_cell(sub_value)


        # Hide unused rows
        self.view.sub_variants_grid_manager.hide_extra_rows(len(switches))

        self.view_model.ensure_editing_switches()


    def update_sub_variant_container(self): #, sub_variants:'SubVariants'):
        self.update_options()
        self.update_switches_container()
        self.view_model.ensure_active_sub_variant()
        