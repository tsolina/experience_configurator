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

    @property 
    def selected_configuration(self) -> 'Configuration':
        return self.get_active_project().active_configuration
    
    @selected_configuration.setter
    def selected_configuration(self, value: 'Configuration'):
        self.get_active_project().active_configuration = value


    def new_configuration(self):
        def add_new_configuration(project:'Project'):
                        
            def on_thread():
                self.selected_configuration = project.configurations.add()
                # self.root_model.application.active_project.active_configuration = self.selected_configuration

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
    
    def update_configuration_name(self, row_id:int, value:str):
        configuration:Configuration = self.get_configuration_by_row_id(row_id)
        configuration.name = value

    def get_state_options(self):
        return Tristate.to_toggle()
    
    def get_look_options(self):
        return self.root_model.application.look_file.targets_list
    
    def get_active_project(self) -> 'Project':
        return self.root_model.application.active_project
    
    def get_configurations(self) -> ObservableList['Configuration']:
        return self.get_active_project().configurations.configuration_collection
    
    def get_configuration_by_row_id(self, index:int) -> 'Configuration':
        return self.get_active_project().configurations.configuration_collection[index]
    
    def get_active_configuration(self) -> 'Configuration':
        project = self.get_active_project()
        return project.active_configuration if project else None

    def get_active_config_var(self) -> tk.StringVar:
        config = self.get_active_configuration()
        if config:
            print(self.__class__.__name__, "get_active_config_var", config.name)
        return config.name_var if config else None