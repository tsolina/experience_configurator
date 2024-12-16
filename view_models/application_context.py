from typing import TYPE_CHECKING

from services.services import Services



if TYPE_CHECKING:
    from application.application import Application
    from view_models.look_editor_view_model import LookEditorViewModel
    from view_models.main_menu_view_model import MainMenuViewModel
    from view_models.main_window_view_model import MainWindowViewModel
    from view_models.variant_editor_view_model import VariantEditorViewModel
    from views.look_editor_view import LookEditorView
    from views.look_editor_event_handler import LookEditorEventHandler
    from views.main_menu_view import MainMenuView
    from views.main_window_view import MainWindowView
    from views.variant_editor_view import VariantEditorView
    from views.variant_editor_event_handler import VariantEditorEventHandler


class ApplicationContext:
    def __init__(self, catia_com):
        self.vm_main_window:'MainWindowViewModel' = None
        self.vm_look_editor:'LookEditorViewModel' = None
        self.vm_variant_editor:'VariantEditorViewModel' = None
        self.vm_main_menu:'MainMenuViewModel' = None

        self.view_main_window:'MainWindowView' = None
        self.view_look_editor:'LookEditorView' = None
        self.view_look_editor_event_handler:'LookEditorEventHandler' = None
        self.view_variant_editor:'VariantEditorView' = None
        self.view_variant_editor_event_handler:'VariantEditorEventHandler' = None
        self.view_main_menu:'MainMenuView' = None

        self.application:'Application' = None
        self.loaded:bool = False

        self._services:Services = None
        self._catia_com = None

    @property
    def services(self):
        if self._services is None:
            if self.application is None:
                raise ValueError("Application must be initialized before accessing services.")
            self._services = Services(self.application, catia_com=self._catia_com)
        return self._services


    def __getattribute__(self, name):
        value = super().__getattribute__(name)
        if value is None:
            print(f"Accessed uninitialized context attribute: {name}")
        return value