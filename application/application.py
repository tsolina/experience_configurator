from inspect import signature
from threading import Thread
from typing import Any, Callable, List, Optional, TYPE_CHECKING


from application.log import Log
from application.look import Look
from application.look_file import LookFile
from application.look_validator import LookValidator
from application.project import Project
from application.projects import Projects
from application.registry_config import RegistryConfig
from application.util import Util
from application.validator import Validator
# import application.experience_extensions # to load once all extensions
from application.xml import XML
import experience as exp



if TYPE_CHECKING:
    from view_models.main_window_view_model import MainWindowViewModel
    from view_models.application_context import ApplicationContext
    from application.get_applied_material import GetAppliedMaterial

class Flags:
    def __init__(self):
        self.no_status_messages = False

class Application():
    VERSION = "Version 0.0.0.1"

    # def __init__(self, parent: 'MainWindowViewModel', catia_com = None):
    def __init__(self, catia_com = None):
        self.context:'ApplicationContext' = None
        self.util = Util(catia_com)
        self._catia = self.util.catia
        self.log = Log(self)
        self.look = Look(self)
        self.look_file = LookFile(self)
        self.look_validator = LookValidator(self)
        self.validator = Validator(self)
        # self.context_menu = CContextMenu(self)
        # self.editors = CEditors(self)
        self.registry: 'RegistryConfig' = RegistryConfig()
        self.flags = Flags()
        # self._shared = _3DxGeneral.App.CShared()
        self._parent: 'MainWindowViewModel' = None # = parent
        self._name: str = "3DExperience Configurator by TSolina"
        self._title: str = self._name
        self._guid: int = 0
        self.disposed_value: bool = False
        self._active_project: 'Project' = None
        self.xml = XML(self)
        self._projects = Projects(self)
        self._active_project_observers:List[Callable[['Project'], None]] = []
        self.is_loading = False

    @property
    def active_project(self) -> 'Project':
        return self._active_project
    
    @active_project.setter
    def active_project(self, value:'Project'):
        if self._active_project != value:
            self._active_project = value
            self.parent.title = self.active_project.name

            # print(self.__class__.__name__, "active_project", self.active_project.configurations, self.active_project.variants)
            # print(__name__, self.context.view_look_editor)
            if self.context.view_look_editor:
                # self.active_project.configurations._notify_observers()
                self.context.vm_look_editor.update_configurations()#self.active_project.configurations)
            if self.context.view_variant_editor:
                # self.active_project.variants._notify_observers()
                self.context.vm_variant_editor.update_variants()#self.active_project.variants)
            


    def add_active_project_observer(self, observer:Callable[['Project'], None]):
        self._active_project_observers.append(observer)

    def _notify_active_project_observers(self):
        for observer in self._active_project_observers:
            observer(self._active_project)

    @property
    def parent(self):
        return self._parent
    
    @parent.setter
    def parent(self, parent:'MainWindowViewModel'):
        self._parent = parent

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def status_message(self) -> str:
        # return self.parent.status_message
        return self.context.services.status.status_message

    @status_message.setter
    def status_message(self, value: str):
        # self.parent.status_update(value)
        self.context.services.status.status_update(value)

    @property
    def error_message(self) -> None:
        # return self.parent.status_message
        return self.context.services.status.status_message

    @error_message.setter
    def error_message(self, value:str = ""):
        if value.startswith("Error:"):
            # self.parent.status_update(value)
            self.context.services.status.status_update(value)
        else:
            # self.parent.status_update(f"Error: {value}")
            self.context.services.status.status_update(f"Error: {value}")

    @property
    def catia(self) -> exp.Application:
        return self._catia
    
    @property
    def projects(self) -> 'Projects':
        return self._projects
    
    @projects.setter
    def projects(self, value:'Projects'):
        self._projects = value
    
    def catia_ready(self, cb: Callable, cb_fail: Optional[Callable[[str], None]] = None):
        if self.util.spec_window_ready():
            cb()
        else:
            if self.catia is None:
                error_msg = "Error: 3Dx is not active"
            else:
                error_msg = "Error: 3Dx has no design window active"
            if cb_fail:
                cb_fail(error_msg)
            else:
                self.error_message = error_msg

    # def ready(self, cb: Callable, cb_fail: Optional[Callable[[str], None]] = None):
    #     def failure_action(msg):
    #         if cb_fail:
    #             cb_fail(msg)
    #         else:
    #             self.status_message = msg
        
    #     self.catia_ready(
    #         lambda: failure_action("Error: No project is currently active") if self.active_project is None else cb(self.active_project),
    #         failure_action
    #     )
    def ready(self, cb: Callable[[Optional[Any]], None], cb_fail: Optional[Callable[[str], None]] = None):
        """
        Ensures the application is in a ready state before executing the provided callback,
        handling callbacks with or without arguments.
        """

        def wrapped_cb(project):
            """
            Wraps the callback to dynamically adjust argument handling.
            """
            cb_params = signature(cb).parameters
            if len(cb_params) == 0:
                # Callback expects no arguments
                cb()
            else:
                # Callback expects at least one argument
                cb(project)

        def failure_action(msg):
            """
            Handles failure scenarios by invoking cb_fail or updating self.status_message.
            """
            if cb_fail:
                cb_fail(msg)
            else:
                self.status_message = msg

        self.catia_ready(
            lambda: failure_action("Error: No project is currently active")
            if self.active_project is None
            else wrapped_cb(self.active_project),
            failure_action
        )



    def project_ready(self, callback:Callable[['Project'], None]):
        def on_status(message:str):
            self.status_message=message

        def on_ready(project:'Project'):
            if self.active_project is None:
                self.error_message = "No project is currently active"
            else:
                callback(self.active_project)
        
        self.ready(on_ready, on_status)

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = f"{self._name} | {value}"

    def selection(self, cb: Callable[[exp.Selection], None], cb_fail: Optional[Callable[[str], None]] = None):
        if self.util.spec_window_ready():
            self.util.cat_select(lambda: cb(self.catia.active_editor().selection()))
        else:
            if cb_fail:
                cb_fail("No Active design app")
            else:
                self.status_message = "No Active design app"    

    def selection_simple(self, cb: Callable[[exp.Selection], None], cb_fail: Optional[Callable[[str], None]] = None):
        if self.util.spec_window_ready():
            cb(self.catia.active_editor().selection())
        else:
            if cb_fail:
                cb_fail("No Active design app")
            else:
                self.status_message = "No Active design app"    

    # def selection(self, 
    #             cb: Callable[[exp.Selection], None], 
    #             cb_fail: Optional[Callable[[str], None]] = None, 
    #             use_cat_select: bool = True):
    #     if self.util.spec_window_ready():
    #         if use_cat_select:
    #             self.util.cat_select(lambda: cb(self.catia.active_editor().selection()))
    #         else:
    #             cb(self.catia.active_editor().selection())
    #     else:
    #         if cb_fail:
    #             cb_fail("No Active design app")
    #         else:
    #             self.status_message = "No Active design app"
            
    @property
    def guid(self) -> int:
        self._guid += 1
        return self._guid

    def sta_thread(self, cb: Callable):
        self.parent.sta_thread(cb)
        # self.view.sta_dispatcher.invoke(lambda: (cb(), self.util.do_events()))

    async def async_task(self, cb: Callable) -> str:
        await cb()
        return "OK"

    def create_task(self, cb: Callable) -> Thread:
        return Thread(target=cb)

    def run_task(self, cb: Callable) -> Thread:
        task = Thread(target=cb)
        task.start()
        return task
    
    def dispose(self):
        if not self.disposed_value:
            # Dispose managed resources
            self.log = None
            self.look_file = None
            self.look_validator = None
            self.validator = None
            self.xml = None
            self.context_menu = None
            # self.editors = None
            self.registry = None
            self.disposed_value = True

    def __del__(self):
        self.dispose()



    # - UI -
    def apply_looks(self):
        def apply_all(project:'Project'):
            self.status_message = "Applying Looks"
            self.look.apply_look_to_all(project)
            self.status_message = "Ready"

        self.project_ready(apply_all)

    def apply_variant(self):
        def apply_variant(project:'Project'):
            self.xml.load_config.activate()

        self.project_ready(apply_variant)

    def get_applied_material(self):
        from application.get_applied_material import GetAppliedMaterial
        GetAppliedMaterial(self)

    def activate_window(self, window:exp.Window):
        window.activate()
        self.projects.activate()

    def process_project_windows(self, callback:Callable[['exp.Window', Callable[['exp.Window'], None]], None]) -> None:
        def on_ready():
            for window in self.catia.windows():                
                if window.com_type() == "SpecsAndGeomWindow":
                    if not window.name().startswith("VIZ_LOOK_LIBRARY"):
                        callback(window, self.activate_window)
        
        def on_fail():
            self.status_message = "processing project windows failed"

        self.catia_ready(on_ready, on_fail)