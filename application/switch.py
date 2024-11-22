from typing import List, Optional

from application.sub_variant import SubVariant
from application.switches import Switches
from application.variant import Variant
from application.variant_type import VariantType
import experience as exp

class Switch:
    def __init__(self, parent: 'Switches'):
        self._parent = parent
        self.application = parent.application
        self._uid = self.application.guid
        self._name = self.__class__.__name__
        self._rtt_uid = None
        self._id = None
        self._type = VariantType.Unknown
        self._actor_collection: List[str] = []
        self._values_collection: List[str] = []
        self._active_value = ""
        self.property_true_value_selection = False
        self._search_list: Optional[List[exp.SelectedElement]] = None

    @property
    def parent(self):
        return self._parent

    @property
    def uid(self) -> int:
        return self._uid

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def rtt_uid(self) -> str:
        if self._rtt_uid is None:
            if self.type_ == VariantType.CodeState:
                self._rtt_uid = self.parent_variant().parent.get_variant(self.name).RttUID
            else:
                my_id = f"{self.uid:04}"
                self._rtt_uid = f"{{12345678-{my_id}-1234-1234-123456789abc}}"
        return self._rtt_uid

    @rtt_uid.setter
    def rtt_uid(self, value: str):
        self._rtt_uid = value

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, value: int):
        self._id = value

    @property
    def type_(self) -> 'VariantType':
        return self._type

    @type_.setter
    def type_(self, value: 'VariantType'):
        self._type = value


    @property
    def actor_collection(self) -> List[str]:
        return self._actor_collection

    @actor_collection.setter
    def actor_collection(self, value: List[str]):
        self._actor_collection = value

    @property
    def values_collection(self) -> List[str]:
        return self._values_collection

    @values_collection.setter
    def values_collection(self, value: List[str]):
        self._values_collection = value

    @property
    def active_value(self) -> str:
        return self._active_value

    @active_value.setter
    def active_value(self, value: str):
        self._active_value = value

    def get_list_of_variants(self) -> List[str]:
        vl = [v.name for v in self.parent.parent.parent.parent.parent.variant_collection if v.name != self.parent.parent.name]
        vl.sort()
        return vl

    def actor_code_style_lmb(self, cb: 'ComboBox') -> 'Switch':
        if not cb.is_dropdown_open:
            self.actor_collection = self.get_list_of_variants()
        return self

    def actor_visibility_key(self, cb: 'ComboBox') -> 'Switch':
        tb: 'TextBox' = cb.template.find_name("PART_EditableTextBox", cb)
        if tb.text:
            self.actor_collection = [tb.text]
            self.name = self.actor_collection[0]
        return self

    def toggle_visible(self) -> 'Switch':
        if self.type_ in (VariantType.Visibility, VariantType.CodeState):
            self.property_true_value_selection = True
            self.active_value = self.values_collection[1] if self.active_value == self.values_collection[0] else self.values_collection[0]
            self.parent.parent.active_switch = self
            self.property_true_value_selection = False
        return self

    def deep_copy(self, subvariant: 'SubVariant') -> 'Switch':
        copy_switch = Switch(subvariant.switches)
        copy_switch.id = self.id
        copy_switch.type_ = self.type_
        copy_switch.name = self.name
        copy_switch.active_value = self.active_value
        copy_switch.values_collection = self.values_collection
        copy_switch.actor_collection = self.actor_collection
        return copy_switch

    @property
    def search_list(self) -> List['exp.SelectedElement']:
        if self._search_list is None:
            self.application.selection(lambda sel: self._initialize_search_list(sel))
        return self._search_list

    @search_list.setter
    def search_list(self, value: List['exp.SelectedElement']):
        self._search_list = value

    def _initialize_search_list(self, selection: exp.Selection):
        selection.search_all(f"Name='{self.name}'")
        self._search_list = selection.to_list()
        selection.clear()

    def parent_variant(self) -> 'Variant':
        return self.parent.parent.parent.parent

    def __eq__(self, other: 'Switch') -> bool:
        return isinstance(other, Switch) and self.uid == other.uid

    def __ne__(self, other: 'Switch') -> bool:
        return not self == other
