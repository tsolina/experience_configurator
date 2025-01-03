from typing import TYPE_CHECKING, Callable, Optional
from application.actor import Actor
from application.actors import Actors
from application.configurations import Configurations
from application.observable_list import ObservableList
from application.tristate import Tristate
from models.look_editor_model import LookEditorModel
import tkinter as tk
from tkinter import ttk
import experience as exp


if TYPE_CHECKING:
    from view_models.application_context import ApplicationContext
    from view_models.main_window_view_model import MainWindowViewModel
    from application.project import Project
    from application.configuration import Configuration

class LookEditorViewModel:
    def __init__(self, context:'ApplicationContext'):
        self.context = context
        self.root_model = self.context.vm_main_window

    @property 
    def selected_configuration(self) -> 'Configuration':
        return self.context.vm_main_window.get_active_project().active_configuration
    
    @selected_configuration.setter
    def selected_configuration(self, value: 'Configuration'):
        self.context.vm_main_window.get_active_project().active_configuration = value


    def new_configuration(self):
        def add_new_configuration(project:'Project'):
                        
            def on_thread():
                self.selected_configuration = project.configurations.add()

            self.root_model.sta_thread(on_thread)

        self.context.services.project.ready(add_new_configuration)

    def clone_configuration(self):
        self.root_model.application.status_message = "Clone is not implemented yet"

    def delete_configuration(self):
        def delete_configuration(project:'Project'):
            project.configurations.delete()

        self.context.services.project.ready(delete_configuration)

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
    
    # def get_active_project(self) -> 'Project':
    #     return self.root_model.application.active_project
    
    def get_configurations(self) -> 'Configurations':
        project = self.context.vm_main_window.get_active_project()
        return project.configurations if project else None
    
    def get_actors(self) -> 'Actors':
        configuration = self.get_active_configuration()
        return configuration.actors if configuration else None
    
    def get_configuration_by_row_id(self, index:int) -> 'Configuration':
        return self.get_configurations()[index]
    
    def get_active_configuration(self) -> 'Configuration':
        project = self.context.vm_main_window.get_active_project()
        return project.active_configuration if project else None

    def get_active_config_var(self) -> tk.StringVar:
        config = self.get_active_configuration()
        return config.name_var if config else None
    
    def update_configurations(self):#, configurations:'Configurations'):
        self.context.view_look_editor_event_handler.update_treeview() #configurations)

    def activate_configuration(self, configuration:'Configuration'):
        self.context.application.active_project.active_configuration = configuration

    def update_actors(self, actors:'Actors'):
        self.context.view_look_editor_event_handler.populate_actors() # actors)

    def activate_actor(self, actor:'Actor'):
        self.context.application.active_project.active_configuration.active_actor = actor

        self.context.services.selection.select_actor(actor.cat_object)

    def get_actor_from_id(self, id:int):
        config = self.get_active_configuration()
        if not config:
            return
        return config.actors[id]

    def select_actor_from_view(self, id:int):
        actor = self.get_actor_from_id(id)
        if not actor:
            return
        
        # self.get_active_configuration().actors.add_actor_to_selection(actor)
        self.context.services.selection.select_actor(actor.cat_object)

    def ensure_active_configuration(self):
        configurations = self.get_configurations()
        if not configurations:
            return
        
        if not self.selected_configuration:
            self.selected_configuration = configurations[-1]

        # self.update_actors()

    def ensure_active_actor(self):
        actors = self.get_actors()
        if not actors:
            return
        
        if not self.selected_configuration.active_actor:
            self.selected_configuration.active_actor = actors[-1]
        
