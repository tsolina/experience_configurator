# task_model.py
from typing import Callable, Any, Optional
import time
import asyncio
from inspect import iscoroutinefunction

class TaskModel:
    def __init__(self, task: Callable[..., Any], *args: Any, **kwargs:Any) -> None:
        """
        Initialize the TaskModel with a task function and any arguments.
        
        :param task: A callable function to be executed.
        :param args: Arguments to be passed to the task function.
        """
        self.task: Callable[..., Any] = task  # The task function
        self.args: tuple = args               # Arguments for the task
        self.kwargs:dict = kwargs
        self.name: Optional[str] = kwargs.pop("name", task.__name__)

    def execute(self) -> Any:
        """Execute the task with the provided arguments."""
        try:
            print(f"Executing task {self.name} with arguments {self.args} and keyword arguments {self.kwargs}")
            if iscoroutinefunction(self.task):
                return asyncio.run(self.task(*self.args, **self.kwargs))
            else:
                return self.task(*self.args, **self.kwargs)
        except Exception as e:
            print(f"Error executing task {self.name}: {e}")
            raise

    def __call__(self) -> Any:
        """Make TaskModel instances callable, delegating to execute."""
        return self.execute()

    def preview(self) -> str:
        """Return a string representation of the task execution."""
        return f"Task: {self.name}, Arguments: {self.args}, Keyword Arguments: {self.kwargs}"