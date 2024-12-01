from application.project import Project
from application.sub_variant import SubVariant
from application.sub_variants import SubVariants
from application.switch import Switch
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
        project = self.context.vm_main_window.get_active_project()
        return project.variants if project else None
    
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

    def activate_switch(self, switch:'Switch'):
        if not switch:
            return
        sv = self.get_editing_sub_variant()
        sv.active_switch = switch

    def activate_editing_sub_variant(self, name:str):
        var = self.get_active_variant()
        if not var:
            return
        
        sv = var.sub_variants.get_sub_variant(name)
        if sv:
            var.editing_sub_variant = sv

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
    
    def get_sub_variant_label_style(self, name:str) -> str:
        editing_sub_variant = self.get_editing_sub_variant()
        if editing_sub_variant and editing_sub_variant.name == name:
            return "Selected.Option.TLabel"
        return "Option.TLabel"
    
    def get_editing_sub_variant(self) -> 'SubVariant':
        variant = self.get_active_variant()
        return variant.editing_sub_variant if variant else None
    
    def is_editing_sub_variant(self, name:str) -> bool:
        editing_sub_variant = self.get_editing_sub_variant()
        if not editing_sub_variant:
            return False
        return editing_sub_variant.name == name
    
    def update_variants(self, variants:'Variants'):
        self.context.view_variant_editor_event_handler.update_variant_container(variants)

    def update_sub_variants(self):
        self.context.view_variant_editor_event_handler.update_sub_variant_container()

    def update_switches_container(self, switches:'Switches'):
        self.context.view_variant_editor_event_handler.update_switches_container()#switches)

    def ensure_active_variant(self):
        variants = self.get_variants()
        if not variants:
            return
        
        if not self.selected_variant:
            self.selected_variant = variants[-1]

        self.update_sub_variants()

    def ensure_active_sub_variant(self):
        sub_variants = self.get_sub_variants()
        if not sub_variants:
            return
        
        if not self.selected_variant:
            self.selected_variant = sub_variants[-1]

    def get_editing_switches(self) -> 'Switches':
        editing_sub_variant = self.get_editing_sub_variant()
        return editing_sub_variant.switches if editing_sub_variant else None
    
    def ensure_editing_switches(self):
        editing_sub_variant = self.get_editing_sub_variant()
        if editing_sub_variant and not editing_sub_variant.active_switch:
            editing_sub_variant.active_switch = editing_sub_variant.switches[-1]


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

    def delete_switch(self):
        def if_project_ready(project:'Project'):
            def add_visible(variant:'Variant'):
                if not variant.editing_sub_variant is None:
                    variant.editing_sub_variant.switches.delete()
                else:
                    self.context.application.error_message("no active sub variant")
            project.variant_ready(add_visible)

        self.root_model.application.project_ready(if_project_ready)

    def on_sub_variant_selected(self, name:str):
        if not name:
            return

        sub_variants = self.get_sub_variants()
        if not sub_variants:
            return
        
        print(self.__class__.__name__, "on_sub_variant", name)
        
        sub_variant = sub_variants.get_sub_variant(name)
        variant = self.get_active_variant()
        if variant.active_sub_variant == sub_variant:
            return
        
        variant.active_sub_variant = sub_variant

        self.context.application.validator.validate(variant)
    # Private Sub LB_SubVariantSelected(sender As Object, e As RoutedEventArgs)
    #     Dim rb As RadioButton = sender
    #     Dim wp As WrapPanel = rb.Content
    #     Dim tb As TextBlock = wp.Children.Item(0)
    #     If tb.Text = vbNullString Then Exit Sub

    #     Dim v As CVariant = App.Model.ActiveProject.ActiveVariant
    #     Dim sv As CSubVariant = v.SubVariants.GetSubVariant(tb.Text)
    #     If v.ActiveSubVariant = sv Then Exit Sub
    #     v.ActiveSubVariant = sv

    #     'Debug.Print("variantSelected:" & v.Name)
    #     App.Validator.Validate(v)
    # End Sub