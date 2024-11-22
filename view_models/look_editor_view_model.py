from typing import TYPE_CHECKING, Callable, Optional
from application.observable_list import ObservableList
from application.tristate import Tristate
from models.look_editor_model import LookEditorModel
import tkinter as tk
from tkinter import ttk

if TYPE_CHECKING:
    from view_models.main_window_view_model import MainWindowViewModel
    from application.project import Project
    from application.configuration import Configuration

class LookEditorViewModel:
    def __init__(self, model: 'LookEditorModel'):
        self._model = model
        self.root_model: 'MainWindowViewModel' = None
        self._selected_configuration: 'Configuration' = None

    @property 
    def selected_configuration(self) -> 'Configuration':
        return self._selected_configuration
    
    @selected_configuration.setter
    def selected_configuration(self, value: 'Configuration'):
        self._selected_configuration = value
        self.root_model.application.active_project.active_configuration = value


    def new_configuration(self):
        def add_new_configuration(project:'Project'):
                        
            def on_thread():
                self.selected_configuration = project.configurations.add()
                self.root_model.application.active_project.active_configuration = self.selected_configuration

            self.root_model.sta_thread(on_thread)

        self.root_model.application.project_ready(add_new_configuration)

    def clone_configuration(self):
        self.root_model.application.status_message = "Clone is not implemented yet"

    def delete_configuration(self):
        def delete_configuration(project:'Project'):
            project.configurations.delete()

        self.root_model.application.project_ready(delete_configuration)

    def activate_project(self):
        app = self.root_model.application
        if not app.active_project:            
            app.projects.activate()

    def get_configuration_by_row_id(self, index:int) -> 'Configuration':
        return self.root_model.application.active_project.configurations.configuration_collection[index]
    
    # def update_configuration_look(self, row_id:int, value:str):
    #     configuration:Configuration = self.get_configuration_by_row_id(row_id)
    #     configuration.active_look = value

    # def update_configuration_active_state(self, row_id:int, value:str):
    #     configuration:Configuration = self.get_configuration_by_row_id(row_id)
    #     configuration.property_true_value_selection = True
    #     configuration.active_look_state = value

    def update_configuration_name(self, row_id:int, value:str):
        configuration:Configuration = self.get_configuration_by_row_id(row_id)
        configuration.name = value

    def get_state_options(self):
        return Tristate.to_toggle()
    
    def get_look_options(self):
        return self.root_model.application.look_file.targets_list