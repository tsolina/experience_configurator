from typing import TYPE_CHECKING
from application.switches import Switches

if TYPE_CHECKING:
    from application.sub_variants import SubVariants
    from application.switch import Switch
    


class SubVariant():
    def __init__(self, parent:'SubVariants', name:str="", switches:'Switches'=None, active_switch:'Switch'=None):
        self._parent = parent
        self.application = parent.application
        self._name = name or self.__class__.__name__
        self._switches = switches or Switches(self)
        self._active_switch = active_switch

    @property
    def parent(self):
        return self._parent

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def switches(self) -> 'Switches':
        return self._switches

    @switches.setter
    def switches(self, value:'Switches'):
        self._switches = value

    @property
    def active_switch(self) -> 'Switch':
        return self._active_switch

    @active_switch.setter
    def active_switch(self, value:'Switch'):
        self._active_switch = value

    def __eq__(self, other:'SubVariant'):
        if isinstance(other, SubVariant):
            return self.name == other.name
        return False

    def __ne__(self, other:'SubVariant'):
        return not self.__eq__(other)
