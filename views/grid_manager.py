from tkinter import ttk
from typing import List, Type

from services.logging_service import LoggingService
from views.cell_data import CellData


class GridManager:
    def __init__(self, container: ttk.Frame, headers: list):
        self.container = container
        self.headers = headers
        self.column_types = [header[2] for header in headers]  # Extract column types
        self.row_widgets = []  # Store widgets for each row

        self._create_headers()

    def _create_headers(self):
        for col_idx, (label, width, _) in enumerate(self.headers):  # Use only label and width
            header_label = ttk.Label(self.container, text=label, anchor="center", relief="raised")
            header_label.grid(row=0, column=col_idx, sticky="nsew", padx=1, pady=1)

            # Set column width
            self.container.columnconfigure(col_idx, minsize=width)

        # self.container.rowconfigure(0, weight=0, minsize=20)

    def add_empty_widget(self, widget_class:Type[ttk.Widget], row_id:int, column_id:int) -> ttk.Widget:
        widget = widget_class(self.container)
        widget.grid(row=row_id, column=column_id, sticky="nsew", padx=1, pady=1)

        widget.grid_forget()
        return widget

    def add_row(self) -> List[ttk.Widget]:
        row_idx = len(self.row_widgets) + 1
        widgets = []

        for col_idx, (_, _, types) in enumerate(self.headers):
        # for col_idx, types in enumerate(self.column_types):
            if not isinstance(types, list):
                widget = self.add_empty_widget(types, row_idx, col_idx)
                widgets.append(widget)
            else:    
                sub_widgets = [self.add_empty_widget(t, row_idx, col_idx) for t in types]
                widgets.append(sub_widgets)

        self.row_widgets.append(widgets)

    def hide_widget(self, widget:ttk.Widget):
        widget.grid_remove()

    def hide_row(self, row_idx: int):
        if 0 < row_idx <= len(self.row_widgets):
            for widget in self.row_widgets[row_idx - 1]:
                if not isinstance(widget, list):
                    widget.grid_remove()
                else:
                    for sub_widget in widget:
                        self.hide_widget(sub_widget)

    def show_row(self, row_idx: int):
        LoggingService.log_point(self, row_idx=row_idx)
        if 0 < row_idx <= len(self.row_widgets):
            for widget in self.row_widgets[row_idx - 1]:
                if isinstance(widget, list):
                    for sub_widget in widget:
                        sub_widget.grid()
                else:
                    widget.grid()

    def get_or_add_row(self, row_idx) -> list:
        """Retrieve an existing row or add a new one if it doesn't exist."""
        # LoggingService.log_point(self, "widget_info.count", current_row=len(self.row_widgets), row_idx=row_idx)
        while len(self.row_widgets) < row_idx:
            # self.add_row([])  # Add empty rows as placeholders
            self.add_row()
        # LoggingService.log_point(self, "widget_info.return", widget=self.row_widgets[row_idx - 1])
        return self.row_widgets[row_idx - 1]

    def get_index(self, to_find, input_list:list):
        index = None
        for i, item in enumerate(input_list):
            if type(item) == to_find:
                index = i
                break

        return index

    def update_cell(self, cell_data:CellData):
        if cell_data.column_id >= len(cell_data.widgets):
            # LoggingService.log_point(self, "creating", widget=cell_data.widget_class)
            widget = self._create_widget(cell_data)
            cell_data.widgets.append(widget)
            widget.grid(row=cell_data.row_id, column=cell_data.column_id, sticky="nsew", **cell_data.grid_options)
        else:
            # LoggingService.log_point(self, "updating", widget=cell_data.widget_class)
            widget = cell_data.widgets[cell_data.column_id]

            if not isinstance(widget, list):
                self._update_widget(widget, cell_data)
                widget.grid(row=cell_data.row_id, column=cell_data.column_id, sticky="nsew", **cell_data.grid_options)
                # LoggingService.log_point(self, "updating_item", widget=widget)
            else:
                # index = widget.index[cell_data.widget_class]
                index = self.get_index(cell_data.widget_class, widget)
                sub_widget = widget[index]
                self._update_widget(sub_widget, cell_data)
                for item_index, item in enumerate(widget):
                    if item_index != index:
                        self.hide_widget(sub_widget)
                sub_widget.grid(row=cell_data.row_id, column=cell_data.column_id, sticky="nsew", **cell_data.grid_options)
                # LoggingService.log_point(self, "updating_list", widget=sub_widget)

        # widget.grid(row=cell_data.row_id, column=cell_data.column_id, sticky="nsew", **cell_data.grid_options)


    def hide_extra_rows(self, active_rows):
        """Hide all rows beyond the active ones."""
        for row_idx in range(active_rows, len(self.row_widgets)):
            self.hide_row(row_idx + 1)

    def hide_all_rows(self):
        """Hide all rows in the grid."""
        for row_idx in range(1, len(self.row_widgets) + 1):
            self.hide_row(row_idx)
    
    def _create_widget(self, cell_data:CellData) -> ttk.Widget:
        widget = cell_data.widget_class(self.container, **cell_data.options)
        return widget

    def _update_widget(self, widget:ttk.Widget, cell_data:CellData):
        for option, value in cell_data.options.items():
            widget.configure(**{option: value})

        for event, handler in cell_data.bind.items():
            widget.bind(event, handler)