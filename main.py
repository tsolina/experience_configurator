import tkinter as tk

from models.main_window_model import MainWindowModel
from view_models.main_window_view_model import MainWindowViewModel
from views.main_window_view import MainWindowView

# from application.experience_extensions import perform_extensions
# perform_extensions()

# import experience as exp

def start(catia_com = None):
    root = tk.Tk()
    root.title("3DExperience Configurator")
    root.geometry("800x450")
    root.configure(bg="SystemButtonFace")

    # Initialize the Model
    model = MainWindowModel(catia_com)

    # Initialize the ViewModel with the Model
    view_model = MainWindowViewModel(root, model)

    # Initialize the View with the ViewModel
    view = MainWindowView(root, view_model)

    root.mainloop()

if __name__ == "__main__":
    start()