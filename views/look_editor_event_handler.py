from typing import TYPE_CHECKING
import tkinter as tk
from tkinter import ttk

from application.actor import Actor
# from application.actors import Actors
from application.actors import Actors
from application.configuration import Configuration
from application.configurations import Configurations
# from application.observable_list import ObservableList
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
        # print(self.__class__.__name__, "config selected:", configuration.name)
        if not configuration:
            return
        self.view_model.activate_configuration(configuration)
        self.populate_actors(configuration.actors)        
        self.view.bind_config_name_var()

    def clear_treeview_widgets(self):
        for widget in self.view.configurations_container.winfo_children():
            widget.destroy()


    def update_treeview(self, configurations:'Configurations'):
        self.clear_treeview_widgets()

        self.view.configurations_container.columnconfigure(0, weight=1)
        frame = ttk.Frame(self.view.configurations_container, style="Standard.TFrame")
        frame.grid(row=1, column=0, sticky="nsew", padx=(6, 3))

        # Define column headers
        headers = [("#", 25), ("Name", 200), ("Look", 120), ("Activated", 88), ("Error", 25)]
        for col_idx, (header, width) in enumerate(headers):
            label = ttk.Label(frame, text=header, anchor="center", relief="raised")
            label.grid(row=0, column=col_idx, sticky="nsew", padx=1, pady=1)

            frame.grid_columnconfigure(col_idx, minsize=width)

        # Configure column weights
        frame.columnconfigure(0, weight=0)  # Adjust column weights as needed
        frame.columnconfigure(1, weight=2)
        frame.columnconfigure(2, weight=1)
        frame.columnconfigure(3, weight=0)
        frame.columnconfigure(4, weight=0)

        # Sample data rows from view model
        # self.context.vm_main_window.activate_project()
        # self.context.vm_look_editor.activate_project()
        configurations = self.view_model.get_configurations()

        self.grid_rows = []  # To store the row widgets for dynamic updates

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

        if len(configurations):
            if not self.view_model.selected_configuration:
                self.view_model.selected_configuration = configurations[-1]

        # Add event bindings for specific actions (e.g., double-click)
        # frame.bind("<Double-1>", self.on_double_click)


    def populate_actors(self, actors:'Actors'):
        for row in self.view.actors_tree.get_children():
            self.view.actors_tree.delete(row)

        for actor in actors:
            self.view.actors_tree.insert("", tk.END, values=(actor.id, actor.name, actor.type_, actor.err_message))

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
    #     selected_item = self.view.tree.selection()
    #     # print(self.__class__.__name__, "Selection changed:", selected_item, type(selected_item))

    #     if not self.view.tree_cb_looks['values']:
    #         targets_list = self.view_model.root_model.application.look_file.targets_list
    #         if targets_list:
    #             self.view.tree_cb_looks['values'] = targets_list
    #     if selected_item:
    #         row_id = self.view.tree.index(selected_item[0])
    #         self.view_model.selected_configuration = self.view_model.get_configuration_by_row_id(row_id)

    def on_actors_selection_change(self, event:tk.Event):
        selected = self.context.view_look_editor.actors_tree.selection()
        if selected:
            row_id = self.context.view_look_editor.actors_tree.index(selected[0])
            self.context.vm_look_editor.select_actor_from_view(row_id)
            # actor = self.context.application.active_project.active_configuration.actors[row_id]
            # print(self.__class__.__name__, "on_selection_change", selected, row_id, actor)

    # Private Sub DG_Editor_SelectionChanged(sender As Object, e As SelectionChangedEventArgs)
    #     Dim dg As DataGrid = sender
    #     If dg.SelectedItem Is Nothing Then Exit Sub

    #     App.Model.Ready(Sub(p)
    #                         p.ActiveConfiguration.ActiveActor = dg.SelectedItem

    #                         App.Selection(Sub(sel)
    #                                           App.Catia.RefreshDisplay = True
    #                                           App.Catia.HSOSynchronized = True

    #                                           If p.ActiveConfiguration.ActiveActor.ErrMessage <> vbNullString Then
    #                                               App.ErrorMessage = p.ActiveConfiguration.ActiveActor.Name & " cannot be selected as it has error: " & p.ActiveConfiguration.ActiveActor.ErrMessage
    #                                           Else
    #                                               sel.ClearEx.Add(p.ActiveConfiguration.ActiveActor.CatObject)
    #                                               App.StatusMessage = "Ready"
    #                                           End If
    #                                       End Sub, Sub(msg) App.StatusMessage = msg)
    #                     End Sub)
    # End Sub