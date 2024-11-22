import tkinter as tk
from tkinter import ttk

def add_tooltip0(self, widget, text):
    # Display tooltip on hover
    tooltip = tk.Toplevel(widget, bg="lightyellow", padx=1, pady=1)
    tooltip.wm_overrideredirect(True)  # Remove window decorations
    tooltip_label = tk.Label(tooltip, text=text, background="lightyellow", borderwidth=1)
    tooltip_label.pack()
    tooltip.withdraw()  # Start hidden

    def on_enter(event):
        tooltip.deiconify()
        x, y, _, _ = widget.bbox("insert")
        tooltip.geometry(f"+{widget.winfo_rootx() + x + 30}+{widget.winfo_rooty() + y + 20}")

    def on_leave(event):
        tooltip.withdraw()

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Menu with Status Bar Example")
        self.geometry("400x300")

        # Create a menu bar
        menubar = tk.Menu(self)
        
        # Create a File menu
        self.file_menu = tk.Menu(menubar, tearoff=0)
        self.file_menu.add_command(label="New", command=self.dummy_command)
        self.file_menu.add_command(label="Open", command=self.dummy_command)
        self.file_menu.add_command(label="Save", command=self.dummy_command)
        
        # Add File menu to menubar
        menubar.add_cascade(label="File", menu=self.file_menu)
        
        # Set the menu bar
        self.config(menu=menubar)

        # Create a status bar
        self.status_text = tk.StringVar()
        self.status_text.set("Ready")  # Default message
        self.status_bar = ttk.Label(self, textvariable=self.status_text, relief="sunken", anchor="w", padding=5)
        self.status_bar.pack(side="bottom", fill="x")

        # Status messages for menu items
        self.status_messages = {
            "New": "Create a new file",
            "Open": "Open an existing file",
            "Save": "Save the current file"
        }

        # Bind motion events to detect menu selection
        self.bind("<Motion>", self.update_status_on_menu_hover)

    def dummy_command(self):
        print("Command executed")

    def update_status_on_menu_hover(self, event):
        """Update status bar based on approximate position over the menu."""
        # Check the active item on the File menu
        active_index = self.file_menu.index("active")

        # Check if an item is actively selected and update the status bar
        if active_index is not None:
            label = self.file_menu.entrycget(active_index, "label")
            if label in self.status_messages:
                self.status_text.set(self.status_messages[label])
        else:
            # Reset the status bar when not hovering over any item
            self.status_text.set("Ready")

if __name__ == "__main__":
    app = Application()
    app.mainloop()
