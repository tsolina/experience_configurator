from typing import Callable
import experience as exp

class Util:
    def __init__(self, catia_com = None):
        self.catia: exp.Application = None
        if catia_com is not None:
            self.catia = exp.Application(catia_com)
        else:
            self.catia = exp.experience_application()

        self._hso_state = False
        self._refresh_state = False

    def is_platform_active(self):
        if self.catia is None:
            return False
        
        if self.catia.windows().count() == 0 or self.catia.editors().count() == 0:
            return False
        
        return True 

    def catia_ready(self, cb, cb_fail, message: str = None):
        if self.catia is None:
            cb_fail(message)
        else:
            cb()

    def ready(self, cb):
        if self.is_platform_active():
            cb()
        return self

    def ready_with_shared(self, cb):
        if self.is_platform_active():
            cb(self)
        return self

    def catia_off(self):
        return self.ready(lambda: self._set_catia_off())

    def _set_catia_off(self):
        self._hso_state = self.catia.hso_synchronized()
        self._refresh_state = self.catia.refresh_display()
        self.catia.refresh_display(False).hso_synchronized(False)

    def catia_on(self):
        return self.ready(lambda: self._set_catia_on())

    def _set_catia_on(self):
        self.catia.refresh_display(self._refresh_state).hso_synchronized(self._hso_state)
        # self.catia.refresh_display(True).hso_synchronized(True)

    def cat_select(self, cb:Callable[[exp.Selection], None]) -> 'Util':
        self.catia_off()
        cb()
        self.catia_on()
        return self

    # @staticmethod
    # def create():
    #     return Util()
    
    def spec_window_ready(self):
        if not self.is_platform_active():
            return False

        if self.catia.windows().count() == 0 or self.catia.editors().count() == 0:
            return False

        if self.catia.active_window().com_type() == "SpecsAndGeomWindow":
            return True

        return False
    
    def do_events(self):
        pass

    