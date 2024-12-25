from tkinter import ttk

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



    def add_row(self, row_data: list):
        row_idx = len(self.row_widgets) + 1
        widgets = []

        for col_idx, data in enumerate(row_data):
            column_type = self.column_types[col_idx]

            if isinstance(column_type, list):
                widget_type = column_type[data]  # Select based on provided index or condition
            else:
                widget_type = column_type

            # Create both label and combobox, but only show the needed one
            label = None
            combobox = None

            if widget_type == 'label':
                label = ttk.Label(self.container, text=data)
                label.grid(row=row_idx, column=col_idx, sticky="nsew", padx=1, pady=1)
                label.grid_remove()  # Initially hide the label
            elif widget_type == 'entry':
                entry = ttk.Entry(self.container)
                entry.insert(0, data)
                entry.grid(row=row_idx, column=col_idx, sticky="nsew", padx=1, pady=1)
                entry.grid_remove()  # Initially hide the entry
            elif widget_type == 'combobox':
                combobox = ttk.Combobox(self.container, values=data)
                combobox.grid(row=row_idx, column=col_idx, sticky="nsew", padx=1, pady=1)
                combobox.grid_remove()  # Initially hide the combobox
            else:
                raise ValueError(f"Unknown widget type: {widget_type}")

            # Store both label and combobox in the widgets list for this row
            widgets.append({"label": label, "entry":entry, "combobox": combobox})

        # Append the widgets to the row_widgets list
        self.row_widgets.append(widgets)

    def hide_row(self, row_idx: int):
        if 0 < row_idx <= len(self.row_widgets):
            for widget in self.row_widgets[row_idx - 1]:
                widget.grid_remove()

    def show_row(self, row_idx: int):
        if 0 < row_idx <= len(self.row_widgets):
            for widget in self.row_widgets[row_idx - 1]:
                widget.grid()

    def get_or_add_row(self, row_idx) -> list:
        """Retrieve an existing row or add a new one if it doesn't exist."""
        # LoggingService.log_point(self, "widget_info.count", current_row=len(self.row_widgets), row_idx=row_idx)
        while len(self.row_widgets) < row_idx:
            self.add_row([])  # Add empty rows as placeholders
        # LoggingService.log_point(self, "widget_info.return", widget=self.row_widgets[row_idx - 1])
        return self.row_widgets[row_idx - 1]


    def update_cell(self, cell_data:CellData):
        if cell_data.column_id >= len(cell_data.widgets):
            widget = self._create_widget(cell_data)
            cell_data.widgets.append(widget)
        else:
            widget = cell_data.widgets[cell_data.column_id]
            self._update_widget(widget, cell_data)

        widget.grid(row=cell_data.row_id, column=cell_data.column_id, sticky="nsew", **cell_data.grid_options)


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