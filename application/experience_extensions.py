from typing import Callable, Optional, overload, TYPE_CHECKING, Protocol
from types import MethodType
from application.util import Util
import experience as exp


if TYPE_CHECKING:
    from extension_typing import HybridBodies

# class SelectionEx(exp.Selection, Protocol):
#     def hide(self) -> 'SelectionEx':
#         ...
#     def show(self) -> 'SelectionEx':
#         ...
#     def search_all(self, search_string:str) -> 'SelectionEx':
#         ...
#     def search_sel(self, search_string:str) -> 'SelectionEx':
#         ...
#     def count_ex(self, cb: Optional[Callable[[exp.Selection], None]] = None,
#                     cb_fail: Optional[Callable[[str], None]] = None,
#                     compare: Optional[Callable[[int, int], bool]] = None,
#                     iVal: Optional[int] = None) -> 'SelectionEx':
#         ...

if not hasattr(exp, "_extensions_applied"):
    if hasattr(exp, "Selection"):
        # Single wrapped function using Optionals
        def count_ex(self: exp.Selection,
                    cb: Optional[Callable[[exp.Selection], None]] = None,
                    cb_fail: Optional[Callable[[str], None]] = None,
                    compare: Optional[Callable[[int, int], bool]] = None,
                    iVal: Optional[int] = None) -> exp.Selection:
            
            # Case 1: Callback only (if count is greater than 0)
            if cb is not None and self.count() > 0:
                cb(self)

            # Case 2: Callback with fail callback (if count is greater than 0, else invoke fail callback)
            elif cb is not None and cb_fail is not None:
                if self.count() > 0:
                    cb(self)
                else:
                    cb_fail("selection empty")

            # Case 3: Callback with comparison function (if comparison is true)
            elif compare is not None and iVal is not None and cb is not None:
                if compare(self.count(), iVal):
                    cb(self)

            # Case 4: Callback with comparison function and fail callback (if comparison is true, else invoke fail callback)
            elif compare is not None and iVal is not None and cb is not None and cb_fail is not None:
                if compare(self.count(), iVal):
                    cb(self)
                else:
                    cb_fail("compare failed")

            return self

        exp.Selection.count_ex = count_ex
        exp.Selection.count_ex.__annotations__ = {
            'self': exp.Selection,
            'cb': Optional[Callable[[exp.Selection], None]],
            'cb_fail': Optional[Callable[[str], None]],
            'compare': Optional[Callable[[int, int], bool]],
            'iVal': Optional[int],
            'return': exp.Selection
        }

        def hide(self:exp.Selection) -> exp.Selection:
            if self.count():
                self.vis_properties().set_show(exp.CatVisPropertyShow.catVisPropertyNoShowAttr)
            return self
        exp.Selection.hide = hide
        exp.Selection.hide.__annotations__ = {'self': exp.Selection}
        
        def show(self:exp.Selection) -> exp.Selection:
            if self.count():
                self.vis_properties().set_show(exp.CatVisPropertyShow.catVisPropertyShowAttr)

            return self
        exp.Selection.show = show
        exp.Selection.show.__annotations__ = {'self': exp.Selection}

        def search_all(self:exp.Selection, search_string:str) -> exp.Selection:
            return self.search(search_string + Util.get_list_separator() + "All")
        exp.Selection.search_all = search_all
        exp.Selection.search_all.__annotations__ = {'self': exp.Selection, 'search_string':str}

        def search_sel(self:exp.Selection, search_string:str) -> exp.Selection:
            return self.search(search_string + Util.get_list_separator() + "Sel")
        exp.Selection.search_sel = search_sel
        exp.Selection.search_sel.__annotations__ = {'self': exp.Selection, 'search_string':str}


    if hasattr(exp, 'HybridBodies'):
        # Overload for the method with no callbacks
        @overload
        def contains(self: 'exp.HybridBodies', name: str) -> bool:
            ...

        # Overload for the method with callbacks
        @overload
        def contains(
            self: 'exp.HybridBodies',
            name: str,
            on_success: Optional[Callable[['exp.HybridBody'], None]] = None,
            on_failure: Optional[Callable[['exp.HybridBodies'], None]] = None
        ) -> 'exp.HybridBodies':
            ...

        # Actual implementation
        def contains(self: 'exp.HybridBodies', name: str, 
                    on_success: Optional[Callable[['exp.HybridBody'], None]] = None,
                    on_failure: Optional[Callable[['exp.HybridBodies'], None]] = None) -> 'exp.HybridBodies | bool':
            # Base check
            exists = name in self.items()

            if on_success or on_failure:
                # If callbacks are provided
                if exists:
                    if on_success:
                        on_success(self.item(name))
                else:
                    if on_failure:
                        on_failure(self)
                return self
            else:
                # Just return the boolean existence check
                return exists

        # Attach the method to the class
        exp.HybridBodies.contains = MethodType(contains, exp.HybridBodies)

    exp._extensions_applied = True


def extend_hybrid_bodies():
    from experience import HybridBody, HybridBodies  # Assuming the class is defined here

    def contains(self, name: str) -> bool:
        return name in self.items()

    def contains_with_callbacks( self: HybridBodies,
                                 name: str,
                                 on_success: Optional[Callable[["HybridBody"], None]] = None,
                                 on_failure: Optional[Callable[["HybridBodies"], None]] = None) -> HybridBodies:
        if self.contains(name):
            if on_success:
                on_success(self.item(name))
        else:
            if on_failure:
                on_failure(self)

        return self

    # Apply the dynamic extension at runtime
    # HybridBodies.contains = contains_with_callbacks
    setattr(exp.HybridBodies, "contains_with_callbacks", contains_with_callbacks)

def perform_extensions():
    extend_hybrid_bodies()

exp.Selection.hide.__annotations__ = {'self': exp.Selection}