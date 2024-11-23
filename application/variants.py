from typing import TYPE_CHECKING, Callable, Optional
from application.observable_list import ObservableList
from application.tristate import Tristate

if TYPE_CHECKING:
    from application.application import Application
    from application.project import Project
    from application.variant import Variant


class Variants(ObservableList['Variant']):
    def __init__(self, parent: 'Project'):
        super().__init__()
        self._parent = parent
        self.application = parent.application
        self._name = self.__class__.__name__

    @property
    def parent(self) -> 'Project':
        return self._parent

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def count(self) -> int:
        return len(self)

    def add_empty_variant(self) -> 'Variant':
        from application.variant import Variant

        new_variant = Variant(self)
        new_variant.id = self.count + 1
        new_variant.name = f"variant.{new_variant.id}"
        new_variant.switch_states = Tristate.to_list()

        def add_variant():
            self.append(new_variant)

        self.application.sta_thread(add_variant)
        new_variant.editing_state = new_variant.active_state
        return new_variant

    def add(self) -> 'Variant':
        new_variant = self.add_empty_variant()

        def select_variant():
            self.application.parent.variant_editor.selected_item = new_variant

        self.application.sta_thread(select_variant)
        self.application.status_message = f"{new_variant.name} added"
        return new_variant

    def add_to_container(self, container: list['Variant']) -> 'Variant':
        from application.variant import Variant

        new_variant = Variant(self)
        new_variant.id = len(container) + 1
        new_variant.name = f"variant.{new_variant.id}"
        new_variant.switch_states = Tristate.to_list()
        new_variant.editing_state = new_variant.active_state

        container.append(new_variant)
        return new_variant

    def clone(self) -> 'Variants':
        def clone_variant(v: 'Variant'):
            cloned_variant = self.add_empty_variant()
            for sub_variant in v.sub_variants.sub_variant_collection:
                for switch in sub_variant.switches.switch_collection:
                    cloned_sub_variant = cloned_variant.sub_variants.get_sub_variant(sub_variant.name)
                    cloned_sub_variant.switches.switch_collection.append(switch.deep_copy(sub_variant))

            cloned_variant.active_state = v.active_state
            cloned_variant.editing_state = cloned_variant.active_state
            self.application.status_message = f"Variant {v.name} cloned"
            self.application.parent.variant_editor.selected_item = cloned_variant

        def clone_failed(msg: str):
            self.application.error_message = f"Clone failed, {msg}"

        self._parent.variant_ready(clone_variant, clone_failed)
        return self

    def delete(self) -> 'Variants':
        def delete_variant(v: 'Variant'):
            active_id = v.id
            self.application.status_message = f"{v.name} deleted"
            self.remove(v)
            self._parent.active_variant = None

            for variant in self:
                if variant.id > active_id:
                    variant.id -= 1

        def delete_failed(msg: str):
            self.application.error_message = f"Delete failed, {msg}"

        self._parent.variant_ready(delete_variant, delete_failed)
        return self

    def delete_variant(self, variant: 'Variant') -> 'Variants':
        active_id = variant.id
        self.application.status_message = f"{variant.name} deleted"
        self.remove(variant)
        self._parent.active_variant = None

        for v in self:
            if v.id > active_id:
                v.id -= 1

        return self

    def for_each(self, callback: Callable[['Variant'], None]):
        for variant in self:
            callback(variant)
        return self

    def get_variant(self, name: str) -> Optional['Variant']:
        return next((variant for variant in self if variant.name == name), None)

    def get_variant_with_callback(self, name: str, callback: Callable[['Variant'], None]):
        variant = self.get_variant(name)
        if variant is None:
            self.application.error_message = f"Variant {name} not found"
        else:
            callback(variant)

    def __del__(self):
        self.clear()
