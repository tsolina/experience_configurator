import tkinter as tk
from tkinter import ttk

# from models.main_window_model import MainWindowModel
from view_models.application_context import ApplicationContext
from view_models.main_window_view_model import MainWindowViewModel
from views.main_window_view import MainWindowView

from application.experience_extensions import *
from application.application import Application
import sys
# perform_extensions
# perform_extensions()

# import experience as exp

def start(catia_com = None):
    root = tk.Tk()
    root.geometry("1000x450")
    root.configure(bg="#C2D5E0")

    context = ApplicationContext(catia_com)
    context.application = Application()
    context.application.context = context

    # Initialize the ViewModel with the Model
    view_model = MainWindowViewModel(root, context) #, catia_com)

    # Initialize the View with the ViewModel
    view = MainWindowView(root, context)
    context.loaded = True

    # x = ttk.Label(root)
    # print("label", dir(x))
    root.mainloop()

if __name__ == "__main__":
    # sys.stderr = open("error.log", "w")
    start()