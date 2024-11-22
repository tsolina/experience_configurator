# task_model.py
from typing import Callable, Any
import time

class TaskModel:
    def __init__(self, task: Callable[..., Any], *args: Any) -> None:
        """
        Initialize the TaskModel with a task function and any arguments.
        
        :param task: A callable function to be executed.
        :param args: Arguments to be passed to the task function.
        """
        self.task: Callable[..., Any] = task  # The task function
        self.args: tuple = args               # Arguments for the task

    def execute(self) -> Any:
        """Execute the task with the provided arguments."""
        print(f"Executing task {self.task.__name__} with arguments {self.args}")
        return self.task(*self.args)  # Call the task function with the arguments
