from typing import List, Dict, Callable
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
import time
import experience as exp

class LookContainer:
    def __init__(self):
        self.variants_list: List[str] = []
        self.variants_dict: Dict[str, 'exp.Material'] = {}
        self.targets_list: List[str] = []
        self.targets_dict: Dict[str, 'exp.Material'] = {}
        self.part: 'exp.Part' = None
        self.err_msg: str = ""

    def __del__(self):
        self.variants_list.clear()
        self.variants_dict.clear()
        self.targets_list.clear()
        self.targets_dict.clear()
        self.part = None

        