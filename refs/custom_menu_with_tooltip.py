import tkinter as tk

class CustomMenu(tk.Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tooltips = {}  # Store tooltips for each menu item

    def add_command(self, label, tooltip=None, **kwargs):
        # Call the original add_command with the provided arguments
        super().add_command(label=label, **kwargs)
        
        # Get the index of the new menu item
        index = self.index("end")  # The last item added
        
        # If a tooltip is provided, store it with the item index
        if tooltip:
            self.tooltips[index] = tooltip
            
            # Bind enter and leave events to show/hide tooltip on hover
            self.bind("<Enter>", lambda e, idx=index: self.show_tooltip(e, idx))
            self.bind("<Leave>", lambda e: self.hide_tooltip())

    def show_tooltip(self, event, index):
        # Display tooltip if it exists for the given index
        if index in self.tooltips:
            tooltip_text = self.tooltips[index]
            self.tooltip = tk.Toplevel(self)
            self.tooltip.wm_overrideredirect(True)
            x = event.x_root + 20
            y = event.y_root + 10
            self.tooltip.geometry(f"+{x}+{y}")
            label = tk.Label(self.tooltip, text=tooltip_text, background="lightyellow", relief="solid", borderwidth=1)
            label.pack()

    def hide_tooltip(self):
        # Hide the tooltip if it exists
        if hasattr(self, "tooltip"):
            self.tooltip.destroy()
            del self.tooltip

# Using CustomMenu in a tkinter application
root = tk.Tk()
root.geometry("300x200")

menubar = CustomMenu(root)
file_menu = CustomMenu(menubar, tearoff=0)

# Adding commands with a custom tooltip argument
file_menu.add_command(label="Open", tooltip="Open a file", command=lambda: print("Open"))
file_menu.add_command(label="Save", tooltip="Save the file", command=lambda: print("Save"))
menubar.add_cascade(label="File", menu=file_menu)
root.config(menu=menubar)

root.mainloop()
