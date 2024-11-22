from application.project import Project
from application.variant import Variant
from models.variant_editor_model import VariantEditorModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from view_models.main_window_view_model import MainWindowViewModel


class VariantEditorViewModel:
    def __init__(self, model: 'VariantEditorModel'):
        self._model = model
        self.root_model: 'MainWindowViewModel' = None
        self._selected_variant: 'Variant' = None

    @property 
    def selected_variant(self) -> 'Variant':
        return self._selected_variant
    
    @selected_variant.setter
    def selected_variant(self, value: 'Variant'):
        self._selected_variant = value

    def new_configuration(self):
        def add_new_variant(project:'Project'):
                        
            def on_thread():
                self.selected_variant = project.variants.add()
                self.root_model.application.active_project.active_variant = self.selected_variant

            self.root_model.sta_thread(on_thread)

        self.root_model.application.project_ready(add_new_variant)