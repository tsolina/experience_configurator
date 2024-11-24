from typing import TYPE_CHECKING



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


class ApplicationContext:
    def __init__(self):
        self.vm_main_window:'MainWindowViewModel' = None
        self.vm_look_editor:'LookEditorViewModel' = None
        self.vm_variant_editor:'VariantEditorViewModel' = None
        self.vm_main_menu:'MainMenuViewModel' = None

        self.view_main_window:'MainWindowView' = None
        self.view_look_editor:'LookEditorView' = None
        self.view_look_editor_event_handler:'LookEditorEventHandler' = None
        self.view_variant_editor:'VariantEditorView' = None
        self.view_main_menu:'MainMenuView' = None

        self.application:'Application' = None