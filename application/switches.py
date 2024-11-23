from typing import TYPE_CHECKING, Callable, List, Optional
from application.observable_list import ObservableList
from application.tristate import Tristate
from application.variant_type import VariantType

import experience as exp

if TYPE_CHECKING:
    from application.sub_variant import SubVariant
    from application.switch import Switch
    from application.look_container import LookContainer


class Switches(ObservableList['Switch']):
    def __init__(self, parent: 'SubVariant'):
        super().__init__()
        self._parent = parent
        self.application = parent.application
        self._name = self.__class__.__name__

    @property
    def parent(self) -> 'SubVariant':
        return self._parent

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    def add_visible(self) -> Optional['Switch']:
        """Adds a visibility switch."""
        new_switch = None
        self.application.ready(lambda: self.application.selection(lambda items: self._add_visibility_switch(items)))
        return new_switch

    def _add_visibility_switch(self, items: List[exp.SelectedElement]):
        """Internal: Handles adding a visibility switch."""
        from application.switch import Switch

        new_switch = Switch(self)
        new_switch.id = len(self) + 1
        new_switch.type_ = VariantType.Visibility
        new_switch.values_collection = Tristate.to_toggle()

        for item in items:
            new_switch.name = item.value(exp.AnyObject).name()
            new_switch.actor_collection = [new_switch.name]
            self.append(new_switch)
            new_switch.search_list = [item]

        if not new_switch:
            new_switch = Switch(self)
            new_switch.id = len(self) + 1
            new_switch.type_ = VariantType.Visibility
            self.append(new_switch)

        self.parent.active_switch = new_switch

        if not self.application.flags.no_status_messages:
            self.application.status_message = "New visibility switch added"

    def add_look(self) -> Optional['Switch']:
        """Adds a look switch."""
        new_switch = None
        self.application.ready(lambda: self._add_look_switch())
        return new_switch

    def _add_look_switch(self):
        """Internal: Handles adding a look switch."""
        from application.switch import Switch

        new_switch = Switch(self)
        new_switch.id = len(self) + 1
        new_switch.type_ = VariantType.Look

        self.application.sta_thread(lambda: self.append(new_switch))
        self.parent.active_switch = new_switch

        self.application.look_file.ready(lambda look: self._assign_look_switch_values(new_switch, look))

        if not self.application.flags.no_status_messages:
            self.application.status_message = "New look switch added"

    def _assign_look_switch_values(self, new_switch: 'Switch', look: 'LookContainer'):
        """Internal: Assigns values to a look switch."""
        new_switch.values_collection = look.variants_list[:]
        new_switch.actor_collection = look.targets_list[:]

    def add_style_code(self) -> Optional['Switch']:
        """Adds a style code switch."""
        new_switch = None
        self.application.ready(lambda: self._add_style_code_switch())
        return new_switch

    def _add_style_code_switch(self):
        """Internal: Handles adding a style code switch."""
        from application.switch import Switch

        new_switch = Switch(self)
        new_switch.id = len(self) + 1
        new_switch.type_ = VariantType.CodeState
        new_switch.values_collection = Tristate.to_toggle()

        self.application.sta_thread(lambda: self.append(new_switch))
        self.parent.active_switch = new_switch

        if not self.application.flags.no_status_messages:
            self.application.status_message = "New style code switch added"

    def delete(self) -> 'Switches':
        """Deletes the currently active switch."""
        active_switch = self.parent.active_switch
        if active_switch is None:
            self.application.error_message = "Delete unsuccessful, no switch selected"
            return self

        active_id = active_switch.id
        self.application.status_message = "Switch deleted"

        self.remove(active_switch)
        self.parent.active_switch = None

        for switch in self:
            if switch.id > active_id:
                switch.id -= 1

        self.application.validator.validate(self.parent.parent.parent)
        return self

    def for_each(self, callback: Callable[['Switch'], None]) -> 'Switches':
        """Executes a callback for each switch."""
        for switch in self:
            callback(switch)
        return self

    def to_list(self) -> List['Switch']:
        """Returns a list of all switches."""
        return list(self)
