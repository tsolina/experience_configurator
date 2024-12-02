from typing import TYPE_CHECKING
import tkinter as tk
from application.flat_variant import FlatVariant
from application.tristate import Tristate
from application.sub_variants import SubVariants

if TYPE_CHECKING:
    from application.sub_variant import SubVariant
    from application.variants import Variants

class Variant():
    def __init__(self, parent: 'Variants', id:str="", name:str="", active_state:str=""):
        self._parent = parent
        self.application = parent.application
        self._uID = self.application.guid
        
        self._active_state = active_state or Tristate.UnknownState
        self._name = name or self.__class__.__name__
        self._rttUID = ""
        self._id = id
        self._switch_states = Tristate.to_list()
        self._sub_variants:'SubVariants' = SubVariants(self)
        self._active_sub_variant:'SubVariant' = self._sub_variants[0]
        self._editing_sub_variant:'SubVariant' = self._active_sub_variant
        # print("SubVariants initialized:", self._sub_variants)
        self._desired_state = Tristate.UnknownState
        self._editing_state = self._active_state # Tristate.UnknownState
        self.property_true_value_selection = False

        self.name_var = tk.StringVar(value=self._name)
        self.active_state_var = tk.StringVar(value=self._active_state)
        self.editing_state_var = tk.StringVar(value=self._editing_state)     

        self.name_var.trace_add("write", self._update_name_from_var)
        self.active_state_var.trace_add("write", self._update_active_state_from_var)
        self.editing_state_var.trace_add("write", self._update_editing_state_from_var)

    def _update_name_from_var(self, *args):
        self.name = self.name_var.get()

    def _update_active_state_from_var(self, *args):
        print(self.__class__.__name__, "update_active_state_var", self.active_state_var.get())
        self.property_true_value_selection = True
        self.active_state = self.active_state_var.get()

    def _update_editing_state_from_var(self, *args):
        self.editing_state = self.editing_state_var.get()

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
    def uID(self):
        return self._uID

    @property
    def RttUID(self):
        if not self._rttUID:
            my_id = f"{self.uID:0000}"
            self._rttUID = f"{{12345678-{my_id}-5678-5678-123456789abc}}"
        return self._rttUID

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    def __eq__(self, to_compare: 'Variant'):
        return isinstance(to_compare, Variant) and self.uID == to_compare.uID

    def __ne__(self, to_compare: 'Variant'):
        return not self.__eq__(to_compare)

    @property
    def switch_states(self):
        return self._switch_states

    @switch_states.setter
    def switch_states(self, value):
        self._switch_states = value

    @property
    def sub_variants(self) -> 'SubVariants':
        return self._sub_variants

    @sub_variants.setter
    def sub_variants(self, value:'SubVariants'):
        self._sub_variants = value

    @property
    def active_sub_variant(self) -> 'SubVariant':
        if not hasattr(self, '_sub_variants'):
            raise AttributeError("_sub_variants has not been initialized or was deleted.")

        return self._active_sub_variant

    @active_sub_variant.setter
    def active_sub_variant(self, value: 'SubVariant'):
        self._active_sub_variant = value
        # if self.editing_sub_variant is None and not value is None:
        #     self.editing_sub_variant = value

        self.application.context.view_variant_editor_event_handler.update_sub_variant_container()#self.sub_variants)

    @property
    def editing_sub_variant(self) -> 'SubVariant':
        # if self.editing_sub_variant is None:
        #     self.editing_sub_variant = self.active_sub_variant
        return self._editing_sub_variant

    @editing_sub_variant.setter
    def editing_sub_variant(self, value:'SubVariant'):
        if self._editing_sub_variant != value:
            self._editing_sub_variant = value

            self.application.context.view_variant_editor_event_handler.update_sub_variant_container()#self.sub_variants)

    @property
    def switches(self):
        return self._sub_variants.get_sub_variant(self._active_state).switches

    @switches.setter
    def switches(self, value):
        self.active_sub_variant.switches = value

    @property
    def desired_switches(self):
        return self._sub_variants.get_sub_variant(self._desired_state).switches

    @desired_switches.setter
    def desired_switches(self, value):
        self.active_sub_variant.switches = value

    @property
    def active_state(self):
        return self._active_state

    @active_state.setter
    def active_state(self, value:str):
        if self._active_state != value:
            self._active_state = value
            # print(self.__class__.__name__, "active_state changed", value)
            # self.sub_variants.active_sub_variant = self.sub_variants.get_sub_variant(value)
            self.active_sub_variant = self.sub_variants.get_sub_variant(value)
            print(self.__class__.__name__, "active_state", value)

    @property
    def desired_state(self):
        return self._desired_state

    @desired_state.setter
    def desired_state(self, value):
        self._desired_state = value

        # what do we do if desired state is different?

    @property
    def editing_state(self):
        return self._editing_state

    @editing_state.setter
    def editing_state(self, value:str):
        def lambda_sub_variant(sub_variant: 'SubVariant'):
            # self._sub_variants.editing_sub_variant = sub_variant
            self.editing_sub_variant = sub_variant

        self._editing_state = value
        sv =  self._sub_variants.get_sub_variant(value)
        if sv:
            lambda_sub_variant(sv)


    def toggle_visible(self):
        self.property_true_value_selection = True

        def lambda_off():
            self._active_state = Tristate.OffState

        def lambda_unknown():
            self._active_state = Tristate.UnknownState

        def lambda_on():
            self._active_state = Tristate.OnState

        def lambda_sub_variant(sub_variant: SubVariant):
            self.active_sub_variant = sub_variant

        if self._active_state == Tristate.OnState:
            flat_variant = FlatVariant(self, Tristate.OnState)
            flat_variant.ready(lambda_off, lambda_unknown)
        elif self._active_state == Tristate.OffState:
            flat_variant = FlatVariant(self, Tristate.OffState)
            flat_variant.ready(lambda_on, lambda_unknown)
        else:
            flat_variant = FlatVariant(self, Tristate.UnknownState)
            flat_variant.ready(lambda_on, lambda_unknown)

        self._sub_variants.get_sub_variant(self._active_state, lambda_sub_variant)
        self.property_true_value_selection = False

        return self

    def __del__(self):
        self._switch_states = None
