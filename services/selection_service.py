from typing import Callable, Optional
import experience as exp
from services.catia_service import CatiaService

class SelectionService:
    def __init__(self, catia_service:CatiaService):
        self.catia_service = catia_service
        self.catia = self.catia_service.catia

        self._hso_state = False
        self._refresh_state = False

    def _catia_active(self, enable: bool) -> None:
        """
        Manage CATIA states.

        Args:
            enable: If True, restore the stored states; if False, disable states and store them.
        """
        if enable:
            # self.catia.refresh_display(self._refresh_state).hso_synchronized(self._hso_state)
            self.catia.refresh_display(True).hso_synchronized(True)
        else:
            self._hso_state = self.catia.hso_synchronized()
            self._refresh_state = self.catia.refresh_display()
            self.catia.refresh_display(False).hso_synchronized(False)

    def cat_select(self, cb:Callable[[exp.Selection], None]) -> 'SelectionService':
        self._catia_active(False)
        cb()
        self._catia_active(True)
        return self
    

    def selection(self, cb: Callable[[exp.Selection], None], cb_fail: Optional[Callable[[str], None]] = None) -> 'SelectionService':
        print(cb)
        self.catia_service.ready(
            lambda: self.cat_select(lambda: cb(self.catia.active_editor().selection())),
            cb_fail
        )        
        return self

    def selection_simple(self, cb: Callable[[exp.Selection], None], cb_fail: Optional[Callable[[str], None]] = None) -> 'SelectionService':
        self.catia_service.ready(
            lambda: cb(self.catia.active_editor().selection()),
            cb_fail
        )        
        return self
    
    def active_selection(self, cb: Callable[[exp.Selection], None], cb_fail: Optional[Callable[[str], None]] = None) -> 'SelectionService':
        def process_active_selection(sel:exp.Selection):
            if sel.count():
                cb(sel)
            else:
                if cb_fail:
                    cb_fail("Selection is empty")

        return self.selection(process_active_selection)
    
    

    def select_actor(self, actor: 'exp.AnyObject') -> 'SelectionService':
        if not actor:
            return self

        return self.selection(lambda sel: sel.clear().add(actor))