from typing import TYPE_CHECKING, Callable, List, Optional
from application.observable_list import ObservableList
from application.tristate import Tristate
from application.variant_type import VariantType

import experience as exp

if TYPE_CHECKING:
    from application.sub_variant import SubVariant
    from application.switch import Switch
    from application.look_container import LookContainer
    from application.project import Project


class Switches(ObservableList['Switch']):
    def __init__(self, parent: 'SubVariant'):
        super().__init__()
        self._parent = parent
        self.application = parent.application
        self._name = self.__class__.__name__

        self.add_observer(self._on_switches_changed)

    def _on_switches_changed(self, new_list: List['Switch']):
        if not self.application.parent or not self.application.context.vm_variant_editor:
            return 

        self.application.context.vm_variant_editor.update_switches_container(new_list)


    @property
    def parent(self) -> 'SubVariant':
        return self._parent

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    def add_visible(self) -> Optional["Switch"]:
        from application.switch import Switch
        new_switch:Optional['Switch'] = None
        def on_project_ready(project:'Project'):
            def on_selection(sel:exp.Selection):
                

                def evaluate_item(item:exp.SelectedElement):
                    nonlocal new_switch
                    new_switch = Switch(self, id=len(self)+1, type_=VariantType.Visibility, name=item.value(exp.AnyObject).name(), selected_item=item)
                    self.append(new_switch)

                    if not new_switch:
                        new_switch = Switch(self, id=len(self)+1, type_=VariantType.Visibility)
                        self.append(new_switch)

                    self.parent.active_switch = new_switch
                    
                    if not self.application.flags:
                        self.application.status_message = "New visibility switch added"

                sel.for_each(lambda item:evaluate_item(item))

            self.application.selection_simple(on_selection)

        self.application.project_ready(on_project_ready)
        return new_switch


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
