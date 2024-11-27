from application.project import Project
from application.sub_variants import SubVariants
from application.switches import Switches
from application.tristate import Tristate
from application.variant import Variant
from application.variants import Variants
from models.variant_editor_model import VariantEditorModel
from typing import TYPE_CHECKING
import tkinter as tk

from view_models.application_context import ApplicationContext

if TYPE_CHECKING:
    from view_models.main_window_view_model import MainWindowViewModel


class VariantEditorViewModel:
    def __init__(self, context:ApplicationContext):
        self.context = context
        self.root_model = self.context.vm_main_window

    @property 
    def selected_variant(self) -> 'Variant':
        return self.context.vm_main_window.get_active_project().active_variant
    
    @selected_variant.setter
    def selected_variant(self, value: 'Variant'):
        self.context.vm_main_window.get_active_project().active_variant = value

    # def get_active_project(self) -> 'Project':
    #     return self.context.application.active_project
    
    def get_variants(self) -> 'Variants':
        return self.context.vm_main_window.get_active_project().variants
    
    def get_active_variant(self) -> 'Variant':
        project = self.context.vm_main_window.get_active_project()
        return project.active_variant if project else None

    def get_active_state(self) -> str:
        # variant = self.get_active_variant()
        # return variant.active_state if variant else None
        # return Tristate.to_toggle()
        return Tristate.to_list()
    
    def activate_variant(self, variant:'Variant'):
        self.context.application.active_project.active_variant = variant

    def get_active_variant_var(self) -> tk.StringVar:
        variant = self.get_active_variant()
        return variant.name_var if variant else None
    
    def get_editing_state_var(self) -> tk.StringVar:
        variant = self.get_active_variant()
        return variant.editing_state_var if variant else None
    
    def get_active_state_var(self) -> tk.StringVar:
        variant = self.get_active_variant()
        return variant.active_state_var if variant else None
    
    def get_sub_variants(self) -> 'SubVariants':
        variant = self.get_active_variant()
        return variant.sub_variants if variant else None
    
    def update_variants(self, variants:'Variants'):
        self.context.view_variant_editor_event_handler.update_variant_container(variants)

    def update_switches_container(self, switches:'Switches'):
        self.context.view_variant_editor_event_handler.update_switches_container(switches)

    def new_variant(self):
        def add_new_variant(project:'Project'):
                        
            def on_thread():
                self.selected_variant = project.variants.add()

            self.root_model.sta_thread(on_thread)

        self.root_model.application.project_ready(add_new_variant)

    def clone_variant(self):
        def clone_variant(project:'Project'):
            project.variants.clone()

        self.context.application.project_ready(clone_variant)

    def delete_variant(self):
        def delete_variant(project:'Project'):
            project.variants.delete()

        self.root_model.application.project_ready(delete_variant)

    def create_new_visibility_switch(self):
        def if_project_ready(project:'Project'):
            def add_visible(variant:'Variant'):
                if not variant.editing_sub_variant is None:
                    variant.editing_sub_variant.switches.add_visible()
                else:
                    self.context.application.error_message("no active sub variant")
            project.variant_ready(add_visible)

        self.root_model.application.project_ready(if_project_ready)
        
    def create_new_look_switch(self):
        def if_project_ready(project:'Project'):
            def add_visible(variant:'Variant'):
                if not variant.editing_sub_variant is None:
                    variant.editing_sub_variant.switches.add_look()
                else:
                    self.context.application.error_message("no active sub variant")
            project.variant_ready(add_visible)

        self.root_model.application.project_ready(if_project_ready)
        
    def new_code_state_switch(self):
        def if_project_ready(project:'Project'):
            def add_visible(variant:'Variant'):
                if not variant.editing_sub_variant is None:
                    variant.editing_sub_variant.switches.add_code_style()
                else:
                    self.context.application.error_message("no active sub variant")
            project.variant_ready(add_visible)

        self.root_model.application.project_ready(if_project_ready)