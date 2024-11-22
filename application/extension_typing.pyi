from typing import TYPE_CHECKING, Callable, Optional
import experience as exp

if TYPE_CHECKING:
    class HybridBodies:
        # def contains(self, name: str) -> bool: ...

        def contains(self, name: str, 
                     on_success: Optional[Callable[["exp.HybridBody"], None]] = None, 
                     on_failure: Optional[Callable[["exp.HybridBodies"], None]] = None) -> bool | "exp.HybridBodies":
            pass  # Only for type checking