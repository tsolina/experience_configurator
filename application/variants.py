from typing import TYPE_CHECKING, Callable
from application.observable_list import ObservableList
from application.tristate import Tristate

if TYPE_CHECKING:
    from application.application import Application
    from application.project import Project
    from application.variant import Variant

class Variants():
    def __init__(self, iParent: 'Project'):
        self._parent = iParent
        self.application = iParent.application
        self._name = self.__class__.__name__
        self._variant_collection:ObservableList[Variant] = ObservableList()
    
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
    def variant_collection(self) -> ObservableList['Variant']:
        return self._variant_collection

    @variant_collection.setter
    def variant_collection(self, value:ObservableList['Variant']):
        self._variant_collection = value

    def count(self) -> int:
        return len(self._variant_collection)

    def add_empty_variant(self):
        new_variant = Variant(self)
        new_variant.id = self.count() + 1
        new_variant.name = f"variant.{new_variant.id}"
        new_variant.switch_states = Tristate.to_list()

        def add_variant():
            self.variant_collection.append(new_variant)

        self.application.sta_thread(add_variant)
        new_variant.editing_state = new_variant.active_state
        return new_variant

    def add(self):
        new_variant = self.add_empty_variant()

        def select_variant():
            # App.Editors.VariantEditor.DG_Main.SelectedItem = new_variant
            self.application.parent.variant_editor.selected_item = new_variant

        self.application.sta_thread(select_variant)
        self.application.status_message = f"{new_variant.name} added"
        return new_variant

    def add_to_container(self, iContainer:list['Variant']):
        new_variant = Variant(self)
        new_variant.id = len(iContainer) + 1
        new_variant.name = f"variant.{new_variant.id}"
        new_variant.switch_states = Tristate.to_list()
        new_variant.editing_state = new_variant.active_state

        iContainer.append(new_variant)
        return new_variant

    def clone(self):
        def clone_variant(v:'Variant'):
            cloned_variant = self.add_empty_variant()
            for sv in v.sub_variants.sub_variant_collection:
                for s in sv.switches.switch_collection:
                    sub_variant = cloned_variant.sub_variants.get_sub_variant(sv.name)
                    sub_variant.switches.switch_collection.append(s.deep_copy(sv))

            cloned_variant.active_state = v.active_state
            cloned_variant.editing_state = cloned_variant.active_state
            self.application.status_message = f"Variant {v.name} cloned"

            # App.Editors.VariantEditor.DG_Main.SelectedItem = cloned_variant
            self.application.parent.variant_editor.selected_item = cloned_variant

        def clone_failed(msg):
            self.application.error_message = f"Clone failed, {msg}"

        self._parent.variant_ready(clone_variant, clone_failed)
        return self

    def delete(self):
        def delete_variant(v: 'Variant'):
            active_id = v.id
            self.application.status_message = f"{v.name} deleted"
            self.variant_collection.remove(v)
            self._parent.active_variant = None

            for vc in self.variant_collection:
                if vc.id > active_id:
                    vc.id -= 1

        def delete_failed(msg):
            self.application.error_message = f"Delete failed, {msg}"

        self._parent.variant_ready(delete_variant, delete_failed)
        return self

    def delete_variant(self, iVariant:'Variant'):
        active_id = iVariant.id
        self.application.status_message = f"{iVariant.name} deleted"
        self.variant_collection.remove(iVariant)
        self._parent.active_variant = None

        for vc in self.variant_collection:
            if vc.id > active_id:
                vc.id -= 1

        return self

    def for_each(self, cb:Callable[['Variant'], None]):
        for v in self._variant_collection:
            cb(v)
        return self

    def get_variant(self, iName) -> 'Variant':
        return next((s for s in self._variant_collection if s.name == iName), None)

    def get_variant_with_callback(self, iName, cb):
        v = self.get_variant(iName)
        if v is None:
            self.application.error_message = f"Variant {iName} not found"
        else:
            cb(v)

    def __del__(self):
        self._variant_collection.clear()
        self._variant_collection = None
