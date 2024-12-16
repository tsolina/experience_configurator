import time
import tkinter as tk
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Callable, List
from application.application import Application
from application.project import Project
from application.projects import Projects
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
    def __init__(self, view_root:tk.Tk, context:ApplicationContext):#, catia_com = None):
        self.context = context
        self.application = self.context.application
        self.application.parent = self
        self.context.vm_main_window = self
        self.context.vm_main_menu = MainMenuViewModel(self.context)
        self.context.vm_look_editor = LookEditorViewModel(self.context)
        self.context.vm_variant_editor = VariantEditorViewModel(self.context)        
        self.view_root = view_root
        self.dispatcher: StaDispatcher = None
        self.task_executor: TaskExecutor = TaskExecutor()
        self.task_list = []

        self.title_var = self.context.services.status.title_var
        self.title_var.trace_add("write", self._update_title_from_var)

    
    def _update_title_from_var(self, *args):
        self.view_root.title(self.title_var.get())

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

    
    def get_active_project(self) -> 'Project':
        return self.context.services.project.get_active_project(self.context.view_main_window.root)


    def update_project(self, projects:'Projects'):
        pass
