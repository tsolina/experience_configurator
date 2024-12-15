from typing import Callable, Optional
import experience as exp

class CatiaService:
    def __init__(self, catia_com):
        self.catia_com = catia_com
        self.catia: exp.Application = exp.Application(catia_com) if catia_com else exp.experience_application()

        self._hso_state = False
        self._refresh_state = False

    def is_platform_active(self):
        if self.catia is None:
            return False
        
        if self.catia.windows().count() == 0 or self.catia.editors().count() == 0:
            return False
        
        return True 

    def spec_window_ready(self):
        if not self.is_platform_active():
            return False

        if self.catia.windows().count() == 0 or self.catia.editors().count() == 0:
            return False

        if self.catia.active_window().com_type() == "SpecsAndGeomWindow":
            return True

        return False

    def catia_ready(self, cb: Callable, cb_fail: Optional[Callable[[str], None]] = None) -> 'CatiaService':
        if self.spec_window_ready():
            cb()
        else:
            if self.catia is None:
                error_msg = "Error: 3Dx is not active"
            else:
                error_msg = "Error: 3Dx has no design window active"
            if cb_fail:
                cb_fail(error_msg)
            else:
                self.error_message = error_msg

        return self


    def _set_catia_off(self):
        self._hso_state = self.catia.hso_synchronized()
        self._refresh_state = self.catia.refresh_display()
        self.catia.refresh_display(False).hso_synchronized(False)

    def catia_off(self):
        return self.catia_ready(lambda: self._set_catia_off())

    def catia_on(self):
        return self.catia_ready(lambda: self._set_catia_on())

    def _set_catia_on(self):
        self.catia.refresh_display(self._refresh_state).hso_synchronized(self._hso_state)
        # self.catia.refresh_display(True).hso_synchronized(True)

    def cat_select(self, cb:Callable[[exp.Selection], None]) -> 'CatiaService':
        self.catia_off()
        cb()
        self.catia_on()
        return self
    

    def selection(self, cb: Callable[[exp.Selection], None], cb_fail: Optional[Callable[[str], None]] = None) -> 'CatiaService':
        if self.spec_window_ready():
            self.cat_select(lambda: cb(self.catia.active_editor().selection()))
        else:
            if cb_fail:
                cb_fail("No Active design app")
            else:
                self.status_message = "No Active design app"    
        
        return self

    def selection_simple(self, cb: Callable[[exp.Selection], None], cb_fail: Optional[Callable[[str], None]] = None) -> 'CatiaService':
        if self.spec_window_ready():
            cb(self.catia.active_editor().selection())
        else:
            if cb_fail:
                cb_fail("No Active design app")
            else:
                self.status_message = "No Active design app" 

        return self