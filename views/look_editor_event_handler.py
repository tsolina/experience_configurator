from typing import TYPE_CHECKING
import tkinter as tk
from tkinter import ttk

from application.actor import Actor
# from application.actors import Actors
from application.actors import Actors
from application.configuration import Configuration
from application.configurations import Configurations
from view_models.application_context import ApplicationContext

if TYPE_CHECKING:
    from view_models.look_editor_view_model import LookEditorViewModel
    from views.look_editor_view import LookEditorView


class LookEditorEventHandler:
    def __init__(self, context:ApplicationContext):
        self.context = context
        self.context.view_look_editor_event_handler = self
        self.view = context.view_look_editor
        self.view_model = context.vm_look_editor
        self.tree_active_row = 0
        self.tree_active_column = 0

    def get_index_from_row_id(self, treeview:ttk.Treeview, row_id:str):
        return treeview.index(row_id)
    
    def on_config_selected(self, configuration:'Configuration'):
        if not configuration:
            return
        self.view_model.activate_configuration(configuration)
        self.populate_actors()#configuration.actors)        
        self.view.bind_config_name_var()

    def clear_container_widgets(self, container:ttk.Frame):
        for widget in container.winfo_children():
            grid_info = widget.grid_info()

            if grid_info.get('row') != 0:
                widget.destroy()

    def clear_treeview_container_widgets(self):
        self.clear_container_widgets(self.view.configurations_frame)

    def clear_actor_frame_widgets(self):
        self.clear_container_widgets(self.view.actors_frame)

    def update_treeview(self):#, configurations:'Configurations'):
        configurations = self.view_model.get_configurations()
        if configurations is None:
            return

        self.clear_treeview_container_widgets()

        self.grid_rows = []  # To store the row widgets for dynamic updates
        frame = self.view.configurations_frame
        # Populate grid rows
        for row_idx, config in enumerate(configurations, start=1):
            # Row ID (label)
            id_label = ttk.Label(frame, text=str(config.id), anchor="center") #, relief="sunken")
            id_label.grid(row=row_idx, column=0, sticky="nsew", padx=1, pady=1)
            id_label.bind("<Button-1>", lambda e, conf=config: self.on_config_selected(conf))


            # Name (entry)
            name_entry = ttk.Entry(frame, textvariable=config.name_var)
            name_entry.grid(row=row_idx, column=1, sticky="nsew", padx=1, pady=1)
            name_entry.bind("<Button-1>", lambda e, conf=config: self.on_config_selected(conf))


            # Look (combobox)
            look_combobox = ttk.Combobox(frame, values=self.view_model.get_look_options(), textvariable=config.active_look_var, width=15)
            look_combobox.grid(row=row_idx, column=2, sticky="nsew", padx=1, pady=1)
            look_combobox.bind("<Button-1>", lambda e, conf=config: self.on_config_selected(conf))


            # Activated (combobox)
            activated_combobox = ttk.Combobox(frame, values=self.view_model.get_state_options(), textvariable=config.active_look_state_var, width=11)
            activated_combobox.grid(row=row_idx, column=3, sticky="nsew", padx=1, pady=1)
            activated_combobox.bind("<Button-1>", lambda e, conf=config: self.on_config_selected(conf))


            # Error (label)
            error_label = ttk.Label(frame, text=config.err_message, anchor="center", relief="sunken")
            error_label.grid(row=row_idx, column=4, sticky="nsew", padx=1, pady=1)
            error_label.bind("<Button-1>", lambda e, conf=config: self.on_config_selected(conf))

            # Store row widgets for future updates
            self.grid_rows.append((id_label, name_entry, look_combobox, activated_combobox, error_label))

        # Configure row weights
        for row_idx in range(len(configurations) + 1):  # +1 for header row
            frame.rowconfigure(row_idx, weight=1)

        self.view_model.ensure_active_configuration()




    def on_actor_selected(self, actor:'Actor'):
        if not actor:
            return
        self.view_model.activate_actor(actor)

    def populate_actors(self):#, configurations:'Configurations'):
        actors = self.view_model.get_actors()
        if actors is None:
            return

        self.clear_actor_frame_widgets()

        self.grid_rows = []  # To store the row widgets for dynamic updates
        frame = self.view.actors_frame
        # Populate grid rows
        for row_idx, actor in enumerate(actors, start=1):
            # Row ID (label)
            id_label = ttk.Label(frame, text=str(actor.id), anchor="center") #, relief="sunken")
            id_label.grid(row=row_idx, column=0, sticky="nsew", padx=1, pady=1)
            id_label.bind("<Button-1>", lambda e, conf=actor: self.on_actor_selected(conf))

            # Name (label)
            actor_name = ttk.Label(frame, textvariable=actor.name_var)
            actor_name.grid(row=row_idx, column=1, sticky="nsew", padx=1, pady=1)
            actor_name.bind("<Button-1>", lambda e, conf=actor: self.on_actor_selected(conf))

            #Type (label)
            type_field = ttk.Label(frame, textvariable=actor.type_var)
            type_field.grid(row=row_idx, column=2, sticky="nsew", padx=1, pady=1)
            type_field.bind("<Button-1>", lambda e, conf=actor: self.on_actor_selected(conf))

            # Error (label)
            error_label = ttk.Label(frame, textvariable=actor.error_message_var, text=actor.err_message)
            error_label.grid(row=row_idx, column=3, sticky="nsew", padx=1, pady=1)
            error_label.bind("<Button-1>", lambda e, conf=actor: self.on_actor_selected(conf))

            # Store row widgets for future updates
            self.grid_rows.append((id_label, actor_name, type_field, error_label))

        # Configure row weights
        for row_idx in range(len(actors) + 1):  # +1 for header row
            frame.rowconfigure(row_idx, weight=0)

        self.view_model.ensure_active_actor()

    def btn_select_actors(self):
        self.context.application.project_ready(
            lambda p: p.config_ready(
                lambda c: c.actors.select_actors()
                )
            )
        
    def btn_deselect_actors(self):
        self.context.application.project_ready(
            lambda p: p.config_ready(
                lambda c: c.actors.deselect_actors()
                )
            )

    def btn_delete_actor(self):
        self.context.application.project_ready(
            lambda p: p.config_ready(
                lambda c: c.actors.delete_actor()
                )
            )


    # def on_actors_selection_change(self, event:tk.Event):
    #     selected = self.context.view_look_editor.actors_tree.selection()
    #     if selected:
    #         row_id = self.context.view_look_editor.actors_tree.index(selected[0])
    #         self.context.vm_look_editor.select_actor_from_view(row_id)
