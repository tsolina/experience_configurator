from typing import Callable, Optional, overload, TYPE_CHECKING
from types import MethodType
import experience as exp


if hasattr(exp, "Selection"):
    def hide(self:exp.Selection) -> exp.Selection:
        return self
    exp.Selection.hide = hide
    
    def show(self:exp.Selection) -> exp.Selection:
        return self
    exp.Selection.show = show

    def search_all(self:exp.Selection, search_string:str) -> exp.Selection:
        return self
    exp.Selection.search_all = search_all


class Test():
    def print_ok(self):
        print("ok")

class Test():
    def print_not_ok(self):
        print("not_ok")

t = Test()
t.print_ok()