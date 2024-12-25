from typing import TYPE_CHECKING, List, Tuple
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
        self.actors_grid_rows: List[Tuple[ttk.Label, ttk.Label, ttk.Label, ttk.Label]] = []
        self.data_grid_rows: List[Tuple[ttk.Label, ttk.Entry, ttk.Combobox, ttk.Combobox, ttk.Label]] = []


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


    def update_treeview(self) -> None:
        configurations = self.view_model.get_configurations()
        if configurations is None:
            return

        # Reuse or create rows as needed
        for row_idx, config in enumerate(configurations, start=1):
            if row_idx > len(self.data_grid_rows):
                # Create a new row if not already available
                self._create_data_row(row_idx, config)

            # Update the existing row with new configuration data
            self._update_data_row(self.data_grid_rows[row_idx - 1], config)

        # Hide any unused rows
        for unused_row in self.data_grid_rows[len(configurations):]:
            self._hide_row(unused_row)

        self.view_model.ensure_active_configuration()

    def _create_data_row(self, row_idx: int, config: 'Configuration') -> None:
        frame = self.view.configurations_frame

        # Create widgets for a row
        id_label = ttk.Label(frame, anchor="center")
        name_entry = ttk.Entry(frame, textvariable=config.name_var)
        look_combobox = ttk.Combobox(
            frame, 
            values=self.view_model.get_look_options(), 
            textvariable=config.active_look_var, 
            width=15
        )
        activated_combobox = ttk.Combobox(
            frame, 
            values=self.view_model.get_state_options(), 
            textvariable=config.active_look_state_var, 
            width=11
        )
        error_label = ttk.Label(frame, anchor="center", relief="sunken")

        # Bind events
        for widget in (id_label, name_entry, look_combobox, activated_combobox, error_label):
            widget.bind("<Button-1>", lambda e, conf=config: self.on_config_selected(conf))

        # Grid the widgets
        id_label.grid(row=row_idx, column=0, sticky="nsew", padx=1, pady=1)
        name_entry.grid(row=row_idx, column=1, sticky="nsew", padx=1, pady=1)
        look_combobox.grid(row=row_idx, column=2, sticky="nsew", padx=1, pady=1)
        activated_combobox.grid(row=row_idx, column=3, sticky="nsew", padx=1, pady=1)
        error_label.grid(row=row_idx, column=4, sticky="nsew", padx=1, pady=1)

        # Store row in the pool
        self.data_grid_rows.append((id_label, name_entry, look_combobox, activated_combobox, error_label))

    def _update_data_row(
        self, 
        row_widgets: Tuple[ttk.Label, ttk.Entry, ttk.Combobox, ttk.Combobox, ttk.Label], 
        config: 'Configuration'
    ) -> None:
        id_label, name_entry, look_combobox, activated_combobox, error_label = row_widgets
        id_label.config(text=str(config.id))
        name_entry.config(textvariable=config.name_var)
        look_combobox.config(values=self.view_model.get_look_options(), textvariable=config.active_look_var)
        activated_combobox.config(values=self.view_model.get_state_options(), textvariable=config.active_look_state_var)
        error_label.config(text=config.err_message)

        # Re-bind events (in case the configuration reference changes)
        for widget in (id_label, name_entry, look_combobox, activated_combobox, error_label):
            widget.bind("<Button-1>", lambda e, conf=config: self.on_config_selected(conf))

        # Show the row if hidden
        for widget in row_widgets:
            widget.grid()

    def _hide_row(self, row_widgets: Tuple[ttk.Label, ttk.Entry, ttk.Combobox, ttk.Combobox, ttk.Label]) -> None:
        # Remove widgets from the grid
        for widget in row_widgets:
            widget.grid_remove()


    def on_actor_selected(self, actor:'Actor'):
        if not actor:
            return
        self.view_model.activate_actor(actor)


    def populate_actors(self) -> None:
        actors = self.view_model.get_actors()
        if actors is None:
            return

        # Reuse or create rows as needed
        for row_idx, actor in enumerate(actors, start=1):
            if row_idx > len(self.actors_grid_rows):
                # Create a new row if not already available
                self._create_actor_row(row_idx, actor)

            # Update the existing row with new actor data
            self._update_actor_row(self.actors_grid_rows[row_idx - 1], actor)

        # Hide any unused rows
        for unused_row in self.actors_grid_rows[len(actors):]:
            self._hide_row(unused_row)

        # Configure row weights
        for row_idx in range(len(actors) + 1):  # +1 for header row
            self.view.actors_frame.rowconfigure(row_idx, weight=0)

    def _create_actor_row(self, row_idx: int, actor: 'Actor') -> None:
        frame = self.view.actors_frame
        # Create widgets for a row
        id_label = ttk.Label(frame, anchor="center")
        actor_name = ttk.Label(frame)
        type_field = ttk.Label(frame)
        error_label = ttk.Label(frame)

        # Bind events
        id_label.bind("<Button-1>", lambda e, conf=actor: self.on_actor_selected(conf))
        actor_name.bind("<Button-1>", lambda e, conf=actor: self.on_actor_selected(conf))
        type_field.bind("<Button-1>", lambda e, conf=actor: self.on_actor_selected(conf))
        error_label.bind("<Button-1>", lambda e, conf=actor: self.on_actor_selected(conf))

        # Grid the widgets
        id_label.grid(row=row_idx, column=0, sticky="nsew", padx=1, pady=1)
        actor_name.grid(row=row_idx, column=1, sticky="nsew", padx=1, pady=1)
        type_field.grid(row=row_idx, column=2, sticky="nsew", padx=1, pady=1)
        error_label.grid(row=row_idx, column=3, sticky="nsew", padx=1, pady=1)

        # Store row in the pool
        self.actors_grid_rows.append((id_label, actor_name, type_field, error_label))

    def _update_actor_row(self, row_widgets: Tuple[ttk.Label, ttk.Label, ttk.Label, ttk.Label], actor: 'Actor') -> None:
        id_label, actor_name, type_field, error_label = row_widgets
        id_label.config(text=str(actor.id))
        actor_name.config(text=actor.name_var.get())
        type_field.config(text=actor.type_var.get())
        error_label.config(text=actor.error_message_var.get())

        # Re-bind events (in case the actor reference changes)
        id_label.bind("<Button-1>", lambda e, conf=actor: self.on_actor_selected(conf))
        actor_name.bind("<Button-1>", lambda e, conf=actor: self.on_actor_selected(conf))
        type_field.bind("<Button-1>", lambda e, conf=actor: self.on_actor_selected(conf))
        error_label.bind("<Button-1>", lambda e, conf=actor: self.on_actor_selected(conf))

        # Show the row if hidden
        for widget in row_widgets:
            widget.grid()

    def _hide_row(self, row_widgets: Tuple[ttk.Label, ttk.Label, ttk.Label, ttk.Label]) -> None:
        # Remove widgets from the grid
        for widget in row_widgets:
            widget.grid_remove()



    def btn_select_actors(self):
        self.context.services.project.ready(
            lambda p: p.config_ready(
                lambda c: c.actors.select_actors()
                )
            )
        
    def btn_deselect_actors(self):
        self.context.services.project.ready(
            lambda p: p.config_ready(
                lambda c: c.actors.deselect_actors()
                )
            )

    def btn_delete_actor(self):
        self.context.services.project.ready(
            lambda p: p.config_ready(
                lambda c: c.actors.delete_actor()
                )
            )