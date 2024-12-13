# extensions.pyi
from typing import Callable, List, Optional
import experience as exp

# Augment exp.Selection with the monkey-patched methods

def count_ex(
    self: exp.Selection,
    cb: Optional[Callable[[exp.Selection], None]] = None,
    cb_fail: Optional[Callable[[str], None]] = None,
    compare: Optional[Callable[[int, int], bool]] = None,
    iVal: Optional[int] = None,
) -> exp.Selection: ...

def hide(self: exp.Selection) -> exp.Selection: ...

def show(self: exp.Selection) -> exp.Selection: ...

def search_all(self: exp.Selection, search_string: str) -> exp.Selection: ...

def search_sel(self: exp.Selection, search_string: str) -> exp.Selection: ...

def to_list(self: exp.Selection) -> List[exp.SelectedElement]: ...
