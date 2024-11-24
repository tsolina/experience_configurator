import time
import tkinter as tk
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Callable, List
from application.application import Application
from application.task_executor import TaskExecutor
from application.task_model import TaskModel
from models.main_window_model import MainWindowModel
import experience as exp
from view_models.application_context import ApplicationContext
from view_models.look_editor_view_model import LookEditorViewModel
from view_models.main_menu_view_model import MainMenuViewModel
from view_models.variant_editor_view_model import VariantEditorViewModel
from views.sta_dispatcher import StaDispatcher

class MainWindowViewModel:
    BASE_TITLE = "3DExperience Configurator"

    # def __init__(self, view_root:tk.Tk, model: 'MainWindowModel', catia_com = None):
    def __init__(self, view_root:tk.Tk, context:ApplicationContext, catia_com = None):
        self.context = context
        self.context.vm_main_window = self
        self.context.vm_look_editor = LookEditorViewModel(self.context)
        self.context.vm_variant_editor = VariantEditorViewModel(self.context)
        self.context.vm_main_menu = MainMenuViewModel(self.context)
        # self._model = model
        self.view_root = view_root
        self.application = Application(self, catia_com)
        self.context.application = self.application
        self.application.context = context
        self.dispatcher: StaDispatcher = None
        self.task_executor: TaskExecutor = TaskExecutor()
        self.task_list = []
        self._title = self.BASE_TITLE
        self._title_observers = []

        self._status_message = tk.StringVar()
        self.status_reset()

        self.current_editor: tk.Frame = None
        self.look_editor: tk.Frame = None
        self.variant_editor: tk.Frame = None

        # self.vm_main_menu: MainMenuViewModel = None
        # self.vm_look_editor: LookEditorViewModel = None
        # self.vm_variant_editor: VariantEditorViewModel = None

    @property
    def status_message(self):
        return self._status_message
    
    def status_update(self, message:str):
        self._status_message.set(message)

    def status_reset(self):
        self._status_message.set("Ready")

    @property
    def title(self) -> str:
        return self._title
    
    @title.setter
    def title(self, value: str):
        new_title = f"{self.BASE_TITLE} {value}"
        # print(self.__class__.__name__, "title:", new_title)
        if self._title != new_title:
            self._title = new_title
            for callback in self._title_observers:
                callback(new_title)

    def add_title_observer(self, callback:Callable[[str], None]):
        self._title_observers.append(callback)



    def look_editor_activate(self):
        self.current_editor.pack_forget()
        self.current_editor = self.look_editor
        self.look_editor.pack(fill='both', expand=True)

    def variant_editor_activate(self):
        self.current_editor.pack_forget()
        self.current_editor = self.variant_editor
        self.variant_editor.pack(fill='both', expand=True)

    def sta_thread(self, callback:Callable):
        # time.sleep(2)
        self.dispatcher.begin_invoke(callback)


    def start_tasks(self, tasks: List[TaskModel], callback:Callable=None) -> None:
        """Execute a list of task models."""
        for task_model in tasks:
            self.task_executor.submit_task(task_model)  # Submit each TaskModel to the executor
        
        # Block until all tasks are completed
        self.task_executor.when_all()
        if callback:
            callback()
        self.task_executor.shutdown()  # Properly shutdown the executor

    def wait_tasks(self, tasks:List[TaskModel]) -> None:
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(task) for task in tasks]

        # Wait for all tasks to complete
        for future in as_completed(futures):
            future.result()  # This will block until the task is complete