from typing import TYPE_CHECKING, Callable, List, Optional, overload
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

        self.add_observer(self._on_variant_changed)

    def _on_variant_changed(self, new_list: List['Variant']):
        # Trigger UI update here
        # print(self.__class__.__name__, "Configuration collection updated:", "updating:", len(new_list), self.application.context.vm_look_editor)

        if not self.application.parent or not self.application.context.vm_variant_editor:
            return 
        # print(self.__class__.__name__, "Configuration collection updated:", len(new_list))
        self.application.context.vm_variant_editor.update_variants(new_list)

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

        id = self.count + 1
        new_variant = Variant(self, id=id, name=f"variant.{id}")
        # new_variant.editing_state = new_variant.active_state

        def add_variant():
            self.append(new_variant)

        self.application.sta_thread(add_variant)        
        return new_variant

    # def add(self) -> 'Variant':
    #     new_variant = self.add_empty_variant()

    #     self.application.status_message = f"{new_variant.name} added"
    #     return new_variant

    # def add_to_container(self, container: list['Variant']) -> 'Variant':
    #     from application.variant import Variant

    #     id = len(container) + 1
    #     new_variant = Variant(self, id=id, name=f"variant.{id}")
    #     # new_variant.editing_state = new_variant.active_state

    #     container.append(new_variant)
    #     return new_variant

    @overload
    def add(self) -> 'Variant':
        ...

    @overload
    def add(self, name:str, active_state:str, container: list['Variant']) -> 'Variant':
        ...

    def add(self, name:str="", active_state:str="", container: Optional[list['Variant']] = None) -> 'Variant':
        """
        Adds a new variant to the application or a specified container.

        Args:
            container (Optional[list[Variant]]): The collection to add the variant to. If None, the variant
                                                 is added to the default application workflow.

        Returns:
            Variant: The created and added variant.
        """
        if container is None:
            # Default add behavior
            variant = self.add_empty_variant()

            self.application.status_message = f"{variant.name} added"
            return variant
        else:
            id = id=len(container)+1

            from application.variant import Variant
            variant = Variant(self, id=id, name=name or f"variant.{id}", active_state=active_state)

            container.append(variant)
            return variant

    def clone(self) -> 'Variants':
        def clone_variant(v: 'Variant'):
            cloned_variant = self.add_empty_variant()
            for sub_variant in v.sub_variants:
                for switch in sub_variant.switches:
                    cloned_sub_variant = cloned_variant.sub_variants.get_sub_variant(sub_variant.name)
                    cloned_sub_variant.switches.append(switch.deep_copy(sub_variant))

            cloned_variant.active_state = v.active_state
            cloned_variant.editing_state = cloned_variant.active_state
            self.application.status_message = f"Variant {v.name} cloned"
            # return cloned_variant
            # self.application.parent.variant_editor.selected_item = cloned_variant
            self.parent.active_variant = cloned_variant

        def clone_failed(msg: str):
            self.application.error_message = f"Clone failed, {msg}"

        self._parent.variant_ready(clone_variant, clone_failed)
        return self
    
    def delete(self) -> 'Variants':
        active_variant = self.parent.active_variant
        if active_variant is None:
            self.application.error_message = "Delete unsuccessful, no variant selected"
            return self

        active_id = active_variant.id
        active_variant.sub_variants.clear()

        index = self.index(active_variant)

        self.parent.active_variant = None
        self.remove(self[index])

        for config in self:
            if config.id > active_id:
                config.id -= 1

        self.application.status_message = "Ready"
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

    # def __del__(self):
    #     self.clear()
