# task_executor.py
from concurrent.futures import ThreadPoolExecutor, Future
import time
from typing import List
from application.task_model import TaskModel

class TaskExecutor:
    def __init__(self) -> None:
        self.executor = ThreadPoolExecutor()  # Initialize the ThreadPoolExecutor
        self.task_list: List[Future] = []

    def submit_task(self, task_model: 'TaskModel') -> None:
        """Submit a TaskModel object to be executed."""
        future = self.executor.submit(task_model.execute)  # Submit the task for execution
        self.task_list.append(future)

    def when_all(self) -> None:
        """Wait for all tasks to complete."""
        while self.task_list:
            completed_task = next((tsk for tsk in self.task_list if tsk.done()), None)
            
            if completed_task:
                self.task_list.remove(completed_task)  # Remove the completed task
            else:
                time.sleep(0.1)  # Avoid 100% CPU usage
        print("All tasks completed!")

    def shutdown(self) -> None:
        """Shuts down the executor."""
        self.executor.shutdown()
