from typing import Callable, Generic, TypeVar, List, Optional, Iterable

T = TypeVar('T')  # Generic type


class ObservableList(Generic[T]):
    def __init__(self, initial_list: Optional[List[T]] = None):
        self._list = initial_list or []
        self._observers: List[Callable[[List[T]], None]] = []

    def _notify_observers(self):
        for observer in self._observers:
            observer(self._list)

    def add_observer(self, callback: Callable[[List[T]], None]):
        self._observers.append(callback)

    # List-like methods
    def append(self, item: T):
        self._list.append(item)
        self._notify_observers()

    def remove(self, item: T):
        self._list.remove(item)
        self._notify_observers()

    def extend(self, items: Iterable[T]):
        self._list.extend(items)
        self._notify_observers()

    def pop(self, index: int = -1) -> T:
        item = self._list.pop(index)
        self._notify_observers()
        return item

    def clear(self):
        self._list.clear()
        self._notify_observers()

    def insert(self, index: int, item: T):
        self._list.insert(index, item)
        self._notify_observers()

    def sort(self, key=None, reverse=False):
        self._list.sort(key=key, reverse=reverse)
        self._notify_observers()

    def reverse(self):
        self._list.reverse()
        self._notify_observers()

    # Index-based updates
    def __setitem__(self, index, value):
        self._list[index] = value
        self._notify_observers()

    def __delitem__(self, index):
        del self._list[index]
        self._notify_observers()

    # Read-only methods that don't modify the list
    def __getitem__(self, index) -> T:
        return self._list[index]

    def __len__(self) -> int:
        return len(self._list)

    def __iter__(self):
        return iter(self._list)

    def __contains__(self, item) -> bool:
        return item in self._list

    def index(self, item: T, *args) -> int:
        return self._list.index(item, *args)

    def count(self, item: T) -> int:
        return self._list.count(item)

    # Optional: Read-only property for external access
    @property
    def list(self) -> List[T]:
        return self._list.copy()  # Return a copy to prevent external modifications

    def __repr__(self) -> str:
        return f"ObservableList({repr(self._list)})"
