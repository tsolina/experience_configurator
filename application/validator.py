from typing import List, Optional, Union, overload, TYPE_CHECKING
from application.flat_variant import FlatVariant
from application.look_container import LookContainer
from application.sub_variant import SubVariant
from application.switch import Switch
from application.tristate import Tristate
from application.variant import Variant
from application.variant_type import VariantType
import experience as exp
# from experience_extensions import *
import application.experience_extensions

if TYPE_CHECKING:   
    from application.application import Application

class Validator():
    def __init__(self, i_parent: 'Application'):
        self._parent = i_parent
        self.application = i_parent
        self._name = self.__class__.__name__
        self._to_show: Optional[List[str]] = None
        self._to_hide: Optional[List[str]] = None
        self._to_show_list: Optional[List[exp.SelectedElement]] = None
        self._to_hide_list: Optional[List[exp.SelectedElement]] = None
        self._do_evaluation = True

    @property
    def parent(self) -> 'Application':
        return self._parent

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value
    
    def _init_validation(self) -> "Validator":
        """
        Initializes validation by resetting lists and synchronizing model states.

        Returns:
            SomeClass: Returns the current instance for chaining.
        """
        self._to_show: List[str] = []
        self._to_hide: List[str] = []
        self._to_show_list: List[exp.SelectedElement] = []
        self._to_hide_list: List[exp.SelectedElement] = []

        # Sync variant desired states with active states
        for variant in self.application.active_project.variants:
            # Uncomment the next line to debug output in Python if necessary:
            # print(f"{variant.name}_{variant.active_state}")
            variant.desired_state = variant.active_state

        # Reset target overrides for LookActors
        for name, look_actor in self.application.active_project.look_actors.items():
            if look_actor.target_override != "":
                look_actor.target_override = ""

        # Disable updates in Catia
        self.application.catia.refresh_display(False).hso_synchronized(False)

        return self

    def _finalize_validation(self) -> "Validator":
        """
        Finalizes the validation process by resetting lists, syncing model states,
        and re-enabling Catia updates.

        Returns:
            Validator: Returns the current instance for chaining.
        """
        # Clear the lists
        self._to_hide.clear()
        self._to_show.clear()
        self._to_show_list.clear()
        self._to_hide_list.clear()

        # Disable evaluation temporarily
        self._do_evaluation = False

        # Sync desired and active states for variants
        for variant in self.application.active_project.variants:
            # Uncomment the next line for debugging output in Python if needed:
            # print(f"states0: {variant.name} -> {variant.active_state} -> {variant.desired_state}")
            if variant.desired_state != variant.active_state:
                variant.active_state = variant.desired_state
            # Uncomment the next line for debugging output in Python:
            # print(f"states1: {variant.name} -> {variant.active_state} -> {variant.desired_state}")

        # Re-enable updates in Catia
        self.application.catia.refresh_display(True).hso_synchronized(True)

        # Re-enable evaluation
        self._do_evaluation = True

        return self


    @overload
    def activate_visible(self, i_variant: 'Variant', i_state: str, i_old: int) -> 'Validator': ...
    
    @overload
    def activate_visible(self, i_variant: 'Variant', i_state: str) -> 'Validator': ...
    
    def activate_visible(self, i_variant: 'Variant', i_state: str, i_old: Optional[int] = None) -> 'Validator':
        def process_switch(s: 'Switch'):
            # Handle Visibility Type
            if s.type_ == VariantType.Visibility:
                if s.active_value == Tristate.OnState:
                    if i_old is not None:
                        _str = f"Name='{s.name}'"
                        if _str not in self._to_show:
                            self._to_show.append(_str)
                    else:
                        for item in s.search_list:
                            self._to_show_list.append(item)
                else:
                    if i_old is not None:
                        _str = f"Name='{s.name}'"
                        if _str not in self._to_hide and _str not in self._to_show:
                            self._to_hide.append(_str)
                    else:
                        for item in s.search_list:
                            self._to_hide_list.append(item)

            # Handle CodeState Type
            elif s.type_ == VariantType.CodeState:
                i_variant.parent.get_variant(
                    s.name, 
                    lambda v: self._process_code_state(v, s.active_value)
                )
        
        # Process all switches for the given subvariant
        i_variant.sub_variants.get_sub_variant(i_state).switches.for_each(process_switch)
        return self

    def _process_code_state(self, variant: 'Variant', active_value: str):
        self.activate_visible(variant, active_value)
        variant.desired_state = active_value

    def activate_look(self, i_variant: 'Variant', i_state: str) -> 'Validator':
        def process_subvariant(sv: 'SubVariant'):
            def process_switch(s: 'Switch'):
                if s.type_ == VariantType.Look:
                    if s.active_value.startswith("t_"):
                        return
                    self.application.look.add_look(s)
                elif s.type_ == VariantType.CodeState:
                    i_variant.parent.get_variant(
                        s.name, lambda v: self.activate_look(v, s.active_value)
                    )

            sv.switches.for_each(process_switch)

        i_variant.sub_variants.get_sub_variant(i_state, process_subvariant)
        return self
    
    def is_state_different(self, i_ref: 'FlatVariant', i_trg: 'FlatVariant') -> bool:
        _result: bool = False

        def check_difference():
            nonlocal _result
            # If there is no overlap, exit early
            if not i_trg.is_overlapping(i_ref):
                return
            # If the two variants are equal, exit early
            if i_ref == i_trg:
                return
            # Otherwise, mark as different
            _result = True

        i_trg.ready(check_difference)
        return _result
    

    def deactivate_different(self, i_variant: 'Variant') -> 'Validator':
        flat_ref = FlatVariant(i_variant, i_variant.desired_state)

        def process_flat_ref(flat_ref_):
            def process_variant(v: 'Variant'):
                if v == i_variant or v.desired_state == Tristate.UnknownState:
                    return

                flat_trg_on = FlatVariant(v, Tristate.OnState)
                flat_trg_off = FlatVariant(v, Tristate.OffState)

                def handle_on_state():
                    def process_on_state(flat_trg_):
                        if self.is_state_different(flat_ref, flat_trg_on):
                            def process_off_state():
                                if self.is_state_different(flat_ref, flat_trg_off):
                                    v.desired_state = Tristate.UnknownState
                                else:
                                    v.desired_state = Tristate.OffState

                            flat_trg_off.ready(process_off_state, lambda: setattr(v, "desired_state", Tristate.OffState))

                    flat_trg_on.ready(process_on_state, lambda: flat_trg_off.ready(
                        lambda: setattr(v, "desired_state", Tristate.OffState) if not self.is_state_different(flat_ref, flat_trg_off)
                        else setattr(v, "desired_state", Tristate.UnknownState),
                        lambda: setattr(v, "desired_state", Tristate.UnknownState)
                    ))

                def handle_off_state():
                    if not v.desired_switches:
                        return

                    def process_off_state():
                        if self.is_state_different(flat_ref, flat_trg_off):
                            v.desired_state = Tristate.UnknownState

                    flat_trg_off.ready(process_off_state, lambda: setattr(v, "desired_state", Tristate.UnknownState))

                if v.desired_state == Tristate.OnState:
                    handle_on_state()
                elif v.desired_state == Tristate.OffState:
                    handle_off_state()

            i_variant.parent.for_each(process_variant)

        flat_ref.ready(process_flat_ref)
        return self


    def activate_same(self, i_variant: 'Variant') -> 'Validator':
        flat_ref = FlatVariant(i_variant, i_variant.desired_state)
        if flat_ref.count() == 0:
            return self

        def process_flat_ref(flat_ref_):
            def process_variant(v: 'Variant'):
                if v == i_variant or v.desired_state == Tristate.OnState:
                    return

                on_ok = False
                flat_trg = FlatVariant(v, Tristate.OnState)

                def check_on_state(flat_ref__):
                    nonlocal on_ok
                    if flat_ref == flat_trg and flat_ref.count() == flat_trg.count():
                        v.desired_state = Tristate.OnState
                        on_ok = True

                flat_trg.ready(check_on_state)

                if on_ok:
                    return

                flat_trg_off = FlatVariant(v, Tristate.OffState)

                def check_off_state():
                    if flat_ref == flat_trg_off and flat_ref.count() == flat_trg.count():
                        v.desired_state = Tristate.OffState

                flat_trg_off.ready(check_off_state)

            i_variant.parent.for_each(process_variant)

        flat_ref.ready(process_flat_ref)
        return self
  
    def is_state_available(self, i_variant: 'Variant', i_state: str) -> bool:
        flat_variant = FlatVariant(i_variant, i_state)
        if flat_variant.count() == 0:
            return True

        result = True

        def process_variant(sv: 'Variant'):
            nonlocal result
            if not result:
                return
            if sv == i_variant:
                return
            if sv.desired_state == Tristate.UnknownState:
                return

            flat_target = FlatVariant(sv, sv.desired_state)
            if self.is_state_different(flat_variant, flat_target):
                result = False

        i_variant.parent.for_each(process_variant)

        return result

    def deactivate_parents(self, i_variant: 'Variant') -> 'Validator':
        def process_parent(sv: 'Variant'):
            if sv == i_variant:
                return

            def process_switch(s: 'Switch'):
                if s.type_ != VariantType.CodeState:
                    return

                def process_variant(v: 'Variant'):
                    if s.active_value == v.desired_state:
                        return

                    if sv.desired_state == Tristate.OnState:
                        # Check if off is valid
                        if not self.is_state_available(sv, sv.desired_state):
                            sv.desired_state = Tristate.UnknownState
                        else:
                            sv.desired_state = Tristate.OffState
                    elif sv.desired_state == Tristate.OffState:
                        sv.desired_state = Tristate.UnknownState
                    elif sv.desired_state == Tristate.UnknownState:
                        pass

                sv.parent.get_variant(s.name, process_variant)

            for switch in sv.desired_switches:
                process_switch(switch)

        i_variant.parent.for_each(process_parent)

        return self


    @overload
    def _validate(self, item: 'Variant') -> 'Validator': 
        ...
    
    @overload
    def _validate(self, item: 'Switch') -> 'Validator': 
        ...
    
    def _validate(self, item: Union['Variant', 'Switch']) -> 'Validator':
        def _validate_variant(i_variant: 'Variant') -> 'Validator':
            if i_variant.desired_state == Tristate.UnknownState:
                return self

            self.deactivate_different(i_variant)
            self.activate_same(i_variant).deactivate_parents(i_variant)
            self.activate_visible(i_variant, i_variant.desired_state).activate_look(i_variant, i_variant.desired_state)
            
            return self
        
        def _validate_switch(i_switch: 'Switch') -> 'Validator':
            if not i_switch.name or not i_switch.active_value:
                return self
            
            if i_switch.parent_variant().active_state == Tristate.UnknownState:
                return self

            if i_switch.type_ == VariantType.Visibility:
                if i_switch.active_value == Tristate.OnState:
                    self._to_show.append(f"Name='{i_switch.name}'")
                else:
                    self._to_hide.append(f"Name='{i_switch.name}'")
            elif i_switch.type_ == VariantType.CodeState:
                i_switch.parent_variant().parent.get_variant(i_switch.name, lambda v: _validate_variant(v))
            elif i_switch.type_ == VariantType.Look:
                if i_switch.name != i_switch.active_value:
                    if i_switch.active_value.startswith("v_"):
                        self.application.look.add_look(i_switch)
            
            self.deactivate_different(i_switch.parent_variant)
            self.activate_same(i_switch.parent_variant()).deactivate_parents(i_switch.parent_variant())

            return self

        if isinstance(item, Variant):
            return _validate_variant(item)
        elif isinstance(item, Switch):
            return _validate_switch(item)
        else:
            raise TypeError("item must be of type Variant or Switch")
        

    def perform_visibility_actions(self) -> 'Validator':
        def _handle_visibility(sel:exp.Selection):
        # def _handle_visibility(sel:SelectionEx):
            if self._to_hide_list:
                sel.clear()
                for item in self._to_hide_list:
                    sel.add(item.value())
                sel.hide().clear()

            if self._to_show_list:
                sel.clear()
                for item in self._to_show_list:
                    sel.add(item.value())
                sel.show().clear()

        self.application.selection_simple(_handle_visibility)
        return self

    def extract_overrides(self) -> 'Validator':
        for v in self.application.active_project.variants:
            for s in v.desired_switches:
                if s.type_ != VariantType.Look:
                    continue
                if not s.active_value or not s.name:
                    continue
                if s.active_value.startswith("v_"):
                    continue

                def on_look_ready(look_container:LookContainer):
                    for name, o_look in self.application.active_project.look_actors.items():
                        if o_look.target_name == s.name:
                            o_look.target_override = s.active_value

                self.application.look_file.ready(on_look_ready)

        return self

    def overrides_available(self) -> bool:
        overrides_available = False

        for v in self.application.active_project.variants:
            if overrides_available:
                break

            for s in v.desired_switches:
                if overrides_available:
                    break

                if s.type_ != VariantType.Look:
                    continue
                if not s.active_value or not s.name:
                    continue
                if s.active_value.startswith("v_"):
                    continue

                overrides_available = True
                break

        return overrides_available

    def apply_overrides(self) -> 'Validator':
        if self.overrides_available():
            self.extract_overrides()
            self.application.look.apply_look_to_all()

        return self


    @overload
    def validate(self, item: "Variant") -> "Validator":
        ...

    @overload
    def validate(self, item: "Switch") -> "Validator":
        ...

    def validate(self, item: Union[Variant, Switch]) -> "Validator":
        """
        Validate the provided Variant or Switch.

        Args:
            item (Variant | Switch): The item to validate.

        Returns:
            Validator: The current validator instance.
        """
        if not self._do_evaluation:
            return self

        self._init_validation()

        if isinstance(item, Variant):
            ref_flat = FlatVariant(item, item.active_state)
            
            def on_ready(ref_flat):
                self._validate(item)
            
            def on_invalid():
                item.active_state = Tristate.UnknownState
                self.application.status_message = f"Variant {item.name} invalid"
            
            ref_flat.ready(on_ready, on_invalid)
        else:
            self._validate(item)

        self.apply_overrides()
        self.perform_visibility_actions()
        self._finalize_validation()

        return self

    def __del__(self):
        self._to_show = None
        self._to_hide = None
