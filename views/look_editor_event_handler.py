from typing import TYPE_CHECKING
import tkinter as tk
from tkinter import ttk

from application.actor import Actor
# from application.actors import Actors
from application.configuration import Configuration
from application.observable_list import ObservableList

if TYPE_CHECKING:
    from view_models.look_editor_view_model import LookEditorViewModel
    from views.look_editor_view import LookEditorView


class LookEditorEventHandler:
    def __init__(self, view:'LookEditorView', view_model:'LookEditorViewModel'):
        self.view = view
        self.view_model = view_model
        self.tree_active_row = 0
        self.tree_active_column = 0

    def get_index_from_row_id(self, treeview:ttk.Treeview, row_id:str):
        return treeview.index(row_id)
    

    def on_look_editor_selection_change(self, event:tk.Event):
        selected_item = self.view.tree.selection()
        print(self.__class__.__name__, "Selection changed:", selected_item, type(selected_item))

        # if not self.view.tree_cb_looks['values']:
        #     targets_list = self.view_model.root_model.application.look_file.targets_list
        #     if targets_list:
        #         self.view.tree_cb_looks['values'] = targets_list

        if selected_item:
            row_id = self.view.tree.index(selected_item[0])
            self.view_model.selected_configuration = self.view_model.get_configuration_by_row_id(row_id)
            selected_config = self.view_model.selected_configuration
            # selected_config.property_true_value_selection = True
            if selected_config:
        #         self.view.tree_cb_looks.config(textvariable=selected_config.active_look_var)
        #         self.view.tree_cb_activate.config(textvariable=selected_config.active_look_state_var)
                self.populate_actors(selected_config.actors.actor_list)

    # def _update_treeview_cb(self, cb:ttk.Combobox):
    #     bbox = self.view.tree.bbox(self.tree_active_row, self.tree_active_column)
    #     if bbox:
    #         cb.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
    #         cb.focus_set()

    #         current_value = self.view.tree.item(self.tree_active_row, "values")[int(self.tree_active_column[1:]) - 1]
    #         cb.set(current_value)

    def on_double_click(self, event:tk.Event):
        # Identify the selected row and column
        region = self.view.tree.identify("region", event.x, event.y)
        if region == "cell":
            row_id = self.view.tree.identify_row(event.y)
            column_id = self.view.tree.identify_column(event.x)
            self.tree_active_row = row_id
            self.tree_active_column = column_id

            if row_id and column_id:
                match column_id:
                    case "#2":
                        x, y, width, height = self.view.tree.bbox(row_id, column_id)
                        cell_value = self.view.tree.item(row_id, "values")[int(column_id[1:]) - 1]

                        entry = self.view.tree_entry_name
                        entry.place(x=x, y=y + self.view.tree.winfo_y(), width=width, height=height)
                        entry.focus_set()

                        entry.value = cell_value

                    # case "#3":
                    #     self._update_treeview_cb(self.view.tree_cb_looks)

                    # case "#4":
                    #     self._update_treeview_cb(self.view.tree_cb_activate)

    def update_cell(self, event:tk.Event):
        new_value = self.view.tree_entry_name.value
        values = list(self.view.tree.item(self.tree_active_row, "values"))
        column_index: int = int(self.tree_active_column[1:]) -1
        values[column_index] = new_value
        self.view.tree.item(self.tree_active_row, values=values)

        if column_index == 1:
            self.view_model.update_configuration_name(self.get_index_from_row_id(self.view.tree, self.tree_active_row), new_value)

        self.view.tree_entry_name.place_forget()

    # def _update_cb_selected(self, cb:ttk.Combobox, callback:callable):
    #     selected_value = cb.get()

    #     if self.tree_active_row and self.tree_active_column:
    #         column = int(self.tree_active_column[1:]) - 1
    #         values = list(self.view.tree.item(self.tree_active_row, "values"))
    #         values[column] = selected_value
    #         self.view.tree.item(self.tree_active_row, values=values)

    #         callback(self.get_index_from_row_id(self.view.tree, self.tree_active_row), selected_value)

    #         cb.place_forget()


    # def on_cb_looks_selected(self, event:tk.Event):
    #     self._update_cb_selected(self.view.tree_cb_looks, self.view_model.update_configuration_look)


    # def on_cb_activate_selected(self, event:tk.Event):
    #     self._update_cb_selected(self.view.tree_cb_activate, self.view_model.update_configuration_active_state)


    def clear_treeview_widgets(self):
        for child in self.view.tree.winfo_children():
            child.place_forget()
            child.destroy()

    def update_treeview(self, configurations:ObservableList['Configuration']):
        self.clear_treeview_widgets()

        self.row_id_mapping = {}
        for row in self.view.tree.get_children():
            self.view.tree.delete(row)

        for idx, configuration in enumerate(configurations, start=1):
            row_id = self.view.tree.insert("", tk.END, values=(
                configuration.id, configuration.name, configuration.active_look_var.get(), configuration.active_look_state_var.get(), configuration.err_message))
            
            self.row_id_mapping[row_id] = idx
            # print(self.__class__.__name__, "update_treeview", row_id)
            # configuration.actors.actor_list.add_observer(self.populate_actors)

        # look_combobox = ttk.Combobox(self.view.tree, values=self.view_model.root_model.application.look_file.targets_list) # values=self.view_model.get_look_options())
        # look_combobox.set(configuration.active_look)
        # look_combobox.grid(row=row_id, column=2)  # Example: Placing combobox in the third column
        # look_combobox.bind("<<ComboboxSelected>>", lambda e, conf=configuration: self.update_configuration_look(conf, look_combobox.get()))

        # state_combobox = ttk.Combobox(self.view.tree, values=self.view_model.get_state_options())
        # state_combobox.set(configuration.active_look_state)
        # state_combobox.grid(row=row_id, column=3)  # Example: Placing combobox in the fourth column
        # state_combobox.bind("<<ComboboxSelected>>", lambda e, conf=configuration: self.update_configuration_active_state(conf, state_combobox.get()))

            # # Create combobox for active_look
            # look_combobox = ttk.Combobox(self.view.tree, values=self.view_model.get_look_options(), textvariable=configuration.active_look_var)
            # look_combobox.grid(row=row_id, column=2)  # Example: Placing combobox in the third column
            # look_combobox.bind("<<ComboboxSelected>>", lambda e, conf=configuration: self.update_configuration_look(conf))

            # # Create combobox for active_look_state
            # state_combobox = ttk.Combobox(self.view.tree, values=self.view_model.get_state_options(), textvariable=configuration.active_look_state_var)
            # state_combobox.grid(row=row_id, column=3)  # Example: Placing combobox in the fourth column
            # state_combobox.bind("<<ComboboxSelected>>", lambda e, conf=configuration: self.update_configuration_active_state(conf))
            
            # # Add observer to ensure updates are reflected in the model
            # configuration.active_look_var.trace_add("write", lambda *args, conf=configuration: self.update_configuration_look(conf))
            # configuration.active_look_state_var.trace_add("write", lambda *args, conf=configuration: self.update_configuration_active_state(conf))

            # # Create combobox for active_look
            # look_combobox = ttk.Combobox(self.view.tree, values=self.view_model.get_look_options(), textvariable=configuration.active_look_var)
            # look_combobox.grid(row=idx, column=2)  # Example: Placing combobox in the third column
            # # Combobox selection automatically updates configuration.active_look via active_look_var

            bbox_look = self.view.tree.bbox(row_id, "#3")  # Column #3
            if bbox_look:
                look_combobox = ttk.Combobox(self.view.tree, values=self.view_model.get_look_options(), textvariable=configuration.active_look_var)
                look_combobox.place(
                    x=bbox_look[0], 
                    y=bbox_look[1] + self.view.tree.winfo_y(), 
                    width=bbox_look[2], 
                    height=bbox_look[3]
                )

            # Create combobox for active_look_state
            # state_combobox = ttk.Combobox(self.view.tree, values=self.view_model.get_state_options(), textvariable=configuration.active_look_state_var)
            # state_combobox.grid(row=idx, column=3)  # Example: Placing combobox in the fourth column
            # # Combobox selection automatically updates configuration.active_look_state via active_look_state_var

            # x, y, width, height = self.view.tree.bbox(row_id, "#4")
            # state_combobox.place(x=x, y=y + self.view.tree.winfo_y(), width=width, height=height)
            bbox_state = self.view.tree.bbox(row_id, "#4")  # Column #4
            if bbox_state:
                state_combobox = ttk.Combobox(self.view.tree, values=self.view_model.get_state_options(), textvariable=configuration.active_look_state_var)
                state_combobox.place(
                    x=bbox_state[0], 
                    y=bbox_state[1] + self.view.tree.winfo_y(), 
                    width=bbox_state[2], 
                    height=bbox_state[3]
                )

            # Add observer to populate actors
            configuration.actors.actor_list.add_observer(self.populate_actors)



    def populate_actors(self, actors:ObservableList['Actor']):
        for row in self.view.actors_tree.get_children():
            self.view.actors_tree.delete(row)

        for actor in actors:
            self.view.actors_tree.insert("", tk.END, values=(actor.id, actor.name, actor.type_, actor.err_message))

    def btn_select_actors(self):
        self.view_model.root_model.application.project_ready(
            lambda p: p.config_ready(
                lambda c: c.actors.select_actors()
                )
            )
        
    def btn_deselect_actors(self):
        self.view_model.root_model.application.project_ready(
            lambda p: p.config_ready(
                lambda c: c.actors.deselect_actors()
                )
            )

    def btn_delete_actor(self):
        self.view_model.root_model.application.project_ready(
            lambda p: p.config_ready(
                lambda c: c.actors.delete_actor()
                )
            )

    def on_actors_selection_change(self, event:tk.Event):
        selected_item = self.view.tree.selection()
        # print(self.__class__.__name__, "Selection changed:", selected_item, type(selected_item))

        if not self.view.tree_cb_looks['values']:
            targets_list = self.view_model.root_model.application.look_file.targets_list
            if targets_list:
                self.view.tree_cb_looks['values'] = targets_list
        if selected_item:
            row_id = self.view.tree.index(selected_item[0])
            self.view_model.selected_configuration = self.view_model.get_configuration_by_row_id(row_id)