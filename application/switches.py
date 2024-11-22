from typing import List, Callable, TYPE_CHECKING
from application.look_container import LookContainer
from application.tristate import Tristate
from application.variant_type import VariantType

import experience as exp
if TYPE_CHECKING:
    from application.sub_variant import SubVariant
    from application.switch import Switch

class Switches():
    def __init__(self, parent: 'SubVariant'):
        self._parent = parent
        self.application = parent.application
        self._name = self.__class__.__name__
        self._switch_collection: list['Switch'] = [] # ObservableCollection()  # Assumes a similar implementation to VB.NET ObservableCollection

    @property
    def parent(self) -> 'SubVariant':
        return self._parent

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def switch_collection(self) -> list['Switch']:# ObservableCollection:
        return self._switch_collection

    @switch_collection.setter
    def switch_collection(self, value: list['Switch']): # ObservableCollection):
        self._switch_collection = value

    @property
    def count(self) -> int:
        return len(self._switch_collection)

    def add_visible(self) -> 'Switch':
        new_switch = None
        self.application.ready(lambda: self.application.selection(lambda s: self._add_visibility_switch(s)))
        return new_switch

    def _add_visibility_switch(self, items:list[exp.SelectedElement]):
        new_switch = Switch(self)
        new_switch.id = len(self._switch_collection) + 1
        new_switch.type_ = VariantType.Visibility
        new_switch.values_collection = Tristate.to_toggle() # ObservableCollection(MTristate.to_toggle)
        
        for item in items:
            new_switch.name = item.value(exp.AnyObject).name()
            new_switch.actor_collection = [new_switch.name] # ObservableCollection([new_switch.name])
            self._switch_collection.append(new_switch)
            new_switch.search_list = [item]

        if not new_switch:
            new_switch = Switch(self)
            new_switch.id = len(self._switch_collection) + 1
            new_switch.type_ = VariantType.Visibility
            self._switch_collection.append(new_switch)
        
        self.parent.active_switch = new_switch

        if not self.application.flags.no_status_messages:
            self.application.status_message = "new visibility switch added"

    def add_look(self) -> 'Switch':
        new_switch = None
        self.application.ready(lambda: self._add_look_switch())
        return new_switch

    def _add_look_switch(self):
        new_switch = Switch(self)
        new_switch.id = len(self._switch_collection) + 1
        new_switch.type_ = VariantType.Look

        self.application.sta_thread(lambda: self._switch_collection.append(new_switch))
        self.parent.active_switch = new_switch

        self.application.look_file.ready(lambda look: self._assign_look_switch_values(new_switch, look))

        if not self.application.flags.no_status_messages:
            self.application.status_message = "new look switch added"

    def _assign_look_switch_values(self, new_switch:'Switch', look:'LookContainer'):
        new_switch.values_collection = look.variants_list[:] # ObservableCollection(look.variants_list)
        new_switch.actor_collection = look.targets_list[:] # ObservableCollection(look.targets_list)

    def add_style_code(self) -> 'Switch':
        new_switch = None
        self.application.ready(lambda: self._add_style_code_switch())
        return new_switch

    def _add_style_code_switch(self):
        new_switch = Switch(self)
        new_switch.id = len(self._switch_collection) + 1
        new_switch.type_ = VariantType.CodeState
        new_switch.values_collection = Tristate.to_toggle() # ObservableCollection(MTristate.to_toggle)

        self.application.sta_thread(lambda: self._switch_collection.append(new_switch))
        self.parent.active_switch = new_switch

        if not self.application.flags.no_status_messages:
            self.application.status_message = "new styleCode switch added"

    def delete(self) -> 'Switches':
        active_switch = self.parent.active_switch
        if active_switch is None:
            self.application.error_message = "Delete unsuccessful, no switch selected"
            return self

        active_id = active_switch.id
        self.application.status_message = "switch deleted"

        self._switch_collection.remove(active_switch)
        self.parent.active_switch = None

        for s in self._switch_collection:
            if s.id > active_id:
                s.id -= 1

        self.application.validator.validate(self.parent.parent.parent)
        return self

    def for_each(self, callback: Callable[['Switch'], None]) -> 'Switches':
        for switch in self._switch_collection:
            callback(switch)
        return self

    def to_list(self) -> List['Switch']:
        #return list(self._switch_collection)
        return self._switch_collection

    def __del__(self):
        self._switch_collection = None
