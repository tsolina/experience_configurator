from typing import TYPE_CHECKING
from view_models.application_context import ApplicationContext
from view_models.main_menu_view_model import MainMenuViewModel
import tkinter as tk

if TYPE_CHECKING:
    from views.main_window_view import MainWindowView

class MainMenuView():
    def __init__(self, root: tk.Tk, context:ApplicationContext):
        self.context = context
        self.context.view_main_menu = self
        self.view_model = context.vm_main_menu

        self.add_main_menu(root)

    def add_main_menu(self, root):
        self.menubar = tk.Menu(root)

        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label='Demo')
        file_menu.add_command(label='Test')
        file_menu.add_separator()
        file_menu.add_command(label='Exit')

        sub_menu = tk.Menu(file_menu, tearoff=0)
        sub_menu.add_command(label='Sub Item')

        file_menu.add_cascade(label='MoreOptions', menu=sub_menu)

        self.menubar.add_cascade(label='File', menu=file_menu)



        project = tk.Menu(self.menubar, tearoff=0)
        project.add_command(label='Reload')
        project.add_separator()
        project.add_command(label='Change default saving location', command=self.view_model.change_default_saving_location) # Change default location where the configurations will be saved

        self.menubar.add_cascade(label='Project', menu=project)


        look_editor = tk.Menu(self.menubar, tearoff=0)
        look_editor.add_command(label='Activate', command=self.view_model.look_editor_activate)
        look_editor.add_command(label='Apply Looks')
        look_editor.add_command(label='Look on selection')
        look_editor.add_separator()
        look_editor.add_command(label='Save', command=self.view_model.look_editor_save)
        look_editor.add_command(label='Load')
        look_editor.add_command(label='Export')
        look_editor.add_command(label='Save')
        look_editor.add_command(label='Remove Looks')
        look_editor.add_command(label='Instantiate missing targets')
        look_editor.add_separator()
        look_editor.add_command(label='Clear')

        self.menubar.add_cascade(label='Look Editor', menu=look_editor)


        variant_editor = tk.Menu(self.menubar, tearoff=0)
        variant_editor.add_command(label='Activate', command=self.view_model.variant_editor_activate)
        variant_editor.add_command(label='Apply Variant')
        variant_editor.add_separator()
        variant_editor.add_command(label='Save', command=self.view_model.variant_editor_save)
        variant_editor.add_command(label='Load', command=self.view_model.variant_editor_load)
        variant_editor.add_command(label='Export')
        variant_editor.add_command(label='Import')
        variant_editor.add_command(label='Deltagen export')

        self.menubar.add_cascade(label='Variant Editor', menu=variant_editor)

        windows_menu = tk.Menu(self.menubar, tearoff=0)
        sub_windows_menu = tk.Menu(file_menu, tearoff=0)
        windows_menu.add_command(label='Activate', command=lambda: self.view_model.windows_activate(sub_windows_menu))
        
        windows_menu.add_cascade(label='Projects', menu=sub_windows_menu)

        self.menubar.add_cascade(label='Windows', menu=windows_menu)

        root.config(menu=self.menubar)