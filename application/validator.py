from typing import overload, TYPE_CHECKING
from application.flat_variant import FlatVariant
from application.switch import Switch
from application.tristate import Tristate
from application.variant import Variant
from application.variant_type import VariantType
import experience as exp

if TYPE_CHECKING:   
    from application.application import Application

class Validator():
    def __init__(self, i_parent: 'Application'):
        self._parent = i_parent
        self.application = i_parent
        self._name = self.__class__.__name__
        self._to_show = [str]
        self._to_hide = [str]
        self._to_show_list = [exp.SelectedElement]
        self._to_hide_list = [exp.SelectedElement]
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

    def _init_validation(self) -> 'Validator':
        self._to_show.clear()
        self._to_hide.clear()
        self._to_show_list.clear()
        self._to_hide_list.clear()

        for variant in self.application.active_project.variants.variant_collection:
            variant.desired_state = variant.active_state

        for name, o_look in self.application.active_project.look_actors.items():
            if o_look.target_override:
                o_look.target_override = ""

        self.application.catia.refresh_display(False).hso_synchronized(False)

        return self

    def _finalize_validation(self) -> 'Validator':
        self._to_hide.clear()
        self._to_show.clear()
        self._to_show_list.clear()
        self._to_hide_list.clear()

        self._do_evaluation = False
        for variant in self.application.active_project.variants.variant_collection:
            if variant.desired_state != variant.active_state:
                variant.desired_state = variant.active_state

        self.application.catia.refresh_display(True).hso_synchronized(True)
        self._do_evaluation = True

        return self
    
    @overload
    def activate_visible(self, variant: 'Variant', state: Tristate, i_old: int = None) -> 'Validator':
        for switch in variant.sub_variants.get_sub_variant(state).switches.switch_collection:
            if switch.type_ == VariantType.Visibility:
                condition_str = f"Name='{switch.name}'"

                if switch.active_value == Tristate.OnState:
                    if condition_str not in self._to_show:
                        self._to_show.append(condition_str)
                else:
                    if condition_str not in self._to_hide and condition_str not in self._to_show:
                        self._to_hide.append(condition_str)

            elif switch.type_ == VariantType.CodeState:
                variant.parent.get_variant(switch.name, lambda v: self.activate_visible(v, switch.active_value))
                variant.desired_state = switch.active_value

        return self
    
    @overload
    def activate_visible(self, variant: 'Variant', state: str) -> 'Validator':
        for switch in variant.sub_variants.get_sub_variant(state).switches.switch_collection:
            if switch.type_ == VariantType.Visibility:
                if switch.active_value == Tristate.OnState:
                    self._to_show_list.extend(switch.search_list)
                else:
                    self._to_hide_list.extend(switch.search_list)

            elif switch.type_ == VariantType.CodeState:
                variant.parent.get_variant(switch.name, lambda v: self.activate_visible(v, switch.active_value))
                variant.desired_state = switch.active_value

        return self
    
    def activate_look(self, variant: 'Variant', state: str) -> 'Validator':
        variant.sub_variants.get_sub_variant(state, lambda sv: [
            self._process_switch(s, variant) for s in sv.switches
        ])
        return self
    
    def _compare_variants(self, ref_variant, target_variant:'Variant', result):
        if target_variant.is_overlapping(ref_variant):
            result = ref_variant != target_variant

    def deactivate_different(self, variant: 'Variant') -> 'Validator':
        flat_ref = FlatVariant(variant, variant.desired_state)
        flat_ref.ready(lambda: self._process_variants_for_deactivation(variant, flat_ref))
        return self
    
    def _process_variants_for_deactivation(self, variant:'Variant', flat_ref):
        for v in variant.parent.variant_collection:
            if v == variant or v.desired_state == Tristate.UnknownState:
                continue
            flat_trg_on = FlatVariant(v, Tristate.OnState)
            flat_trg_off = FlatVariant(v, Tristate.OffState)

            if v.desired_state == Tristate.OnState:
                self._update_desired_state_on(flat_ref, flat_trg_on, flat_trg_off, v)
            elif v.desired_state == Tristate.OffState and v.desired_switches:
                self._update_desired_state_off(flat_ref, flat_trg_off, v)

    def _update_desired_state_on(self, flat_ref, flat_trg_on, flat_trg_off, v):
        flat_trg_on.ready(lambda: self._evaluate_on_state(flat_ref, flat_trg_on, flat_trg_off, v))

    def _evaluate_on_state(self, flat_ref, flat_trg_on, flat_trg_off, v):
        if self.is_state_different(flat_ref, flat_trg_on):
            flat_trg_off.ready(lambda: self._determine_off_state(flat_ref, flat_trg_off, v))

    def _determine_off_state(self, flat_ref, flat_trg_off, v:'Variant'):
        if self.is_state_different(flat_ref, flat_trg_off):
            v.desired_state = Tristate.UnknownState
        else:
            v.desired_state = Tristate.OffState        

    def activate_same(self, variant: 'Variant') -> 'Validator':
        flat_ref = FlatVariant(variant, variant.desired_state)
        if flat_ref.count() == 0:
            return self
        flat_ref.ready(lambda: self._process_variants_for_activation(variant, flat_ref))
        return self

    def _process_variants_for_activation(self, variant:'Variant', flat_ref):
        for v in variant.parent.variant_collection:
            if v == variant or v.desired_state == Tristate.OnState:
                continue
            flat_trg = FlatVariant(v, Tristate.OnState)
            self._check_activation(flat_ref, flat_trg, v)

    def _compare_for_activation(self, flat_ref, flat_trg, v:'Variant', _on_ok):
        if flat_ref == flat_trg and flat_ref.count() == flat_trg.count():
            v.desired_state = Tristate.OnState
            _on_ok = True

        if not _on_ok:
            flat_trg_off = FlatVariant(v, Tristate.OffState)
            flat_trg_off.ready(lambda: self._set_off_state(flat_ref, flat_trg_off, v))

    def _set_off_state(self, flat_ref:FlatVariant, flat_trg_off:FlatVariant, v:'Variant'):
        if flat_ref == flat_trg_off and flat_ref.count() == flat_trg_off.count():
            v.desired_state = Tristate.OffState

    def is_state_available(self, variant: 'Variant', state: str) -> bool:
        flat_variant = FlatVariant(variant, state)
        if flat_variant.count() == 0:
            return True

        result = True
        for sv in variant.parent.variant_collection:
            if not result or sv == variant or sv.desired_state == Tristate.UnknownState:
                continue

            flat_target = FlatVariant(sv, sv.desired_state)
            if self.is_state_different(flat_variant, flat_target):
                result = False
                break
        return result   

    def deactivate_parents(self, variant: 'Variant') -> 'Validator':
        for sv in variant.parent.variant_collection:
            if sv == variant:
                continue
            for s in sv.desired_switches.switch_collection:
                if s.type_ != VariantType.CodeState:
                    continue
                sv.parent.get_variant(s.name, lambda v: self._evaluate_parent(sv, s, v))
        return self
    
    def _evaluate_parent(self, sv:'Variant', s:'Switch', v:'Variant'):
        if s.active_value == v.desired_state:
            return

        if sv.desired_state == Tristate.OnState:
            sv.desired_state = Tristate.OffState if self.is_state_available(sv, sv.desired_state) else Tristate.UnknownState
        elif sv.desired_state == Tristate.OffState:
            sv.desired_state = Tristate.UnknownState

    def _validate(self, variant: 'Variant') -> 'Validator':
        if variant.desired_state == Tristate.UnknownState:
            return self

        self.deactivate_different(variant)
        self.activate_same(variant).deactivate_parents(variant)
        self.activate_visible(variant, variant.desired_state).activate_look(variant, variant.desired_state)

        return self
    
    def perform_visibility_actions(self, i_old: int) -> 'Validator':
        self.application.selection(lambda sel: self._execute_visibility_actions(sel, self._to_hide, self._to_show), lambda msg: setattr(self.application, 'status_message', msg))
        return self

    def _execute_visibility_actions(self, sel, to_hide, to_show):
        if to_hide:
            sel.search_all(f"({' + '.join(to_hide)})").hide().clear()
        if to_show:
            sel.search_all(f"({' + '.join(to_show)})").show().clear()

    def perform_visibility_actions_simple(self) -> 'Validator':
        self.application.selection(lambda sel: self._execute_visibility_list_actions(sel))
        return self
    
    def _execute_visibility_list_actions(self, sel:exp.Selection):
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

    def perform_visibility_actions_with_callback(self, cb: callable):
        self.application.selection(lambda sel: self._execute_async_visibility_actions(sel, cb), lambda msg: setattr(self.application, 'error_message', msg))

    def _execute_async_visibility_actions(self, sel:exp.Selection, cb):
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor() as executor:
            if self._to_hide:
                executor.submit(lambda: sel.search_all(f"({' + '.join(self._to_hide)})").hide().clear())
            cb()
            if self._to_show:
                executor.submit(lambda: sel.search_all(f"({' + '.join(self._to_show)})").show().clear())

    def extract_overrides(self) -> 'Validator':
        for variant in self.application.active_project.variants.variant_collection:
            for s in variant.desired_switches.switch_collection:
                if s.type_ != VariantType.Look or not s.active_value or not s.name or s.active_value.startswith("v_"):
                    continue
                self.application.look_file.ready(lambda look: self._set_override_for_look(s))
        return self

    def _set_override_for_look(self, s:'Switch'):
        for name, o_look in self.application.active_project.look_actors.items():
            if o_look.target_name == s.name:
                o_look.target_override = s.active_value
                print(f"override: {s.name}")

    def overrides_available(self) -> bool:
        for variant in self.application.active_project.variants.variant_collection:
            for s in variant.desired_switches.switch_collection:
                if s.type_ == VariantType.Look and s.active_value and s.name and not s.active_value.startswith("v_"):
                    return True
        return False

    def apply_overrides(self) -> 'Validator':
        if self.overrides_available():
            print("overrides available")
            self.extract_overrides()
            self.application.look.apply_look_to_all()
        return self
    
    def deactivate_parents(self, variant: 'Variant') -> 'Validator':
        for sv in variant.parent.variant_collection:
            if sv == variant:
                continue
            for s in sv.desired_switches.switch_collection:
                if s.type_ != VariantType.CodeState:
                    continue
                sv.parent.get_variant(s.name, lambda v: self._evaluate_parent(sv, s, v))
        return self
    
    def _evaluate_parent(self, sv:'Variant', s:'Switch', v:Variant):
        if s.active_value == v.desired_state:
            return

        if sv.desired_state == Tristate.OnState:
            sv.desired_state = Tristate.OffState if self.is_state_available(sv, sv.desired_state) else Tristate.UnknownState
        elif sv.desired_state == Tristate.OffState:
            sv.desired_state = Tristate.UnknownState

    def _validate(self, variant: 'Variant') -> 'Validator':
        if variant.desired_state == Tristate.UnknownState:
            return self

        self.deactivate_different(variant)
        self.activate_same(variant).deactivate_parents(variant)
        self.activate_visible(variant, variant.desired_state).activate_look(variant, variant.desired_state)

        return self
    
    def perform_visibility_actions(self, i_old: int = None) -> 'Validator':
        self.application.selection(lambda sel: self._execute_visibility_actions(sel, self._to_hide, self._to_show), lambda msg: setattr(self.application, 'status_message', msg))
        return self

    def _execute_visibility_actions(self, sel, to_hide, to_show):
        if to_hide:
            sel.search_all(f"({' + '.join(to_hide)})").hide().clear()
        if to_show:
            sel.search_all(f"({' + '.join(to_show)})").show().clear()

    def perform_visibility_actions_simple(self) -> 'Validator':
        self.application.selection(lambda sel: self._execute_visibility_list_actions(sel))
        return self

    def _execute_visibility_list_actions(self, sel:exp.Selection):
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

    def validate(self, i_variant: 'Variant') -> 'Validator':
        if not self._do_evaluation:
            return self

        self._init_validation()

        ref_flat = FlatVariant(i_variant, i_variant.active_state)
        ref_flat.ready(
            lambda: self._validate(i_variant),
            lambda: self._handle_invalid_variant(i_variant)
        )

        self.apply_overrides()
        self.perform_visibility_actions()
        self._finalize_validation()

        return self
    
    def _handle_invalid_variant(self, i_variant:'Variant'):
        i_variant.active_state = Tristate.UnknownState
        self.application.status_message = f"variant {i_variant.name} invalid" 
    
    def _validate_switch(self, i_switch: 'Switch') -> 'Validator':
        if not i_switch.name or not i_switch.active_value or i_switch.parent_variant().active_state == Tristate.UnknownState:
            return self

        if i_switch.type_ == VariantType.Visibility:
            if i_switch.active_value == Tristate.OnState:
                self._to_show.append(f"Name='{i_switch.name}'")
            else:
                self._to_hide.append(f"Name='{i_switch.name}'")
        elif i_switch.type_ == VariantType.CodeState:
            i_switch.parent_variant().parent.get_variant(
                i_switch.name, 
                lambda v: self._update_variant_state(v, i_switch)
            )
        elif i_switch.type_ == VariantType.Look and i_switch.name != i_switch.active_value:
            if i_switch.active_value.startswith("v_"):
                self.application.look.add_look(i_switch)

        self.deactivate_different(i_switch.parent_variant())
        self.activate_same(i_switch.parent_variant()).deactivate_parents(i_switch.parent_variant())

        return self
    
    def _update_variant_state(self, v:'Variant', i_switch:'Switch'):
        v.active_state = i_switch.active_value
        self._validate(v)

    def validate_switch(self, i_switch: 'Switch') -> 'Validator':
        self._init_validation()
        self._validate_switch(i_switch)
        self.apply_overrides()
        self.perform_visibility_actions()
        self._finalize_validation()
        return self


    def _process_switch(self, switch:'Switch', variant:'Variant'):
        if switch.type_ == VariantType.Look:
            if not switch.active_value.startswith("t_"):
                self.application.look.add_look(switch)
        elif switch.type_ == VariantType.CodeState:
            variant.parent.get_variant(switch.name, lambda v: self.activate_look(v, switch.active_value))

    def is_state_different(self, ref_variant: 'FlatVariant', target_variant: 'FlatVariant') -> bool:
        result = False
        target_variant.ready(lambda: self._compare_variants(ref_variant, target_variant, result))
        return result



    def deactivate_parents(self, variant: 'Variant') -> 'Validator':
        for sv in variant.parent.variant_collection:
            if sv == variant:
                continue
            for s in sv.desired_switches.switch_collection:
                if s.type_ != VariantType.CodeState:
                    continue
                sv.parent.get_variant(s.name, lambda v: self._evaluate_parent(sv, s, v))
        return self

    def _evaluate_parent(self, sv:'Variant', s:'Switch', v:'Variant'):
        if s.active_value == v.desired_state:
            return

        if sv.desired_state == Tristate.OnState:
            sv.desired_state = Tristate.OffState if self.is_state_available(sv, sv.desired_state) else Tristate.UnknownState
        elif sv.desired_state == Tristate.OffState:
            sv.desired_state = Tristate.UnknownState

    def _validate(self, variant: 'Variant') -> 'Validator':
        if variant.desired_state == Tristate.UnknownState:
            return self

        self.deactivate_different(variant)
        self.activate_same(variant).deactivate_parents(variant)
        self.activate_visible(variant, variant.desired_state).activate_look(variant, variant.desired_state)

        return self

    @overload
    def perform_visibility_actions(self, i_old: int = None) -> 'Validator':
        self.application.selection(lambda sel: self._execute_visibility_actions(sel, self._to_hide, self._to_show), lambda msg: setattr(self.application, 'status_message', msg))
        return self

    def _execute_visibility_actions(self, sel, to_hide, to_show):
        if to_hide:
            sel.search_all(f"({' + '.join(to_hide)})").hide().clear()
        if to_show:
            sel.search_all(f"({' + '.join(to_show)})").show().clear()

    @overload
    def perform_visibility_actions(self) -> 'Validator':
        self.application.selection(lambda sel: self._execute_visibility_list_actions(sel))
        return self

    def _execute_visibility_list_actions(self, sel: exp.Selection):
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

    def validate(self, i_variant: 'Variant') -> 'Validator':
        if not self._do_evaluation:
            return self

        self._init_validation()

        ref_flat = FlatVariant(i_variant, i_variant.active_state)
        ref_flat.ready(
            lambda: self._validate(i_variant),
            lambda: self._handle_invalid_variant(i_variant)
        )

        self.apply_overrides()
        self.perform_visibility_actions()
        self._finalize_validation()

        return self

    def _handle_invalid_variant(self, i_variant:'Variant'):
        i_variant.active_state = Tristate.UnknownState
        self.application.status_message = f"variant {i_variant.name} invalid"

    def _validate_switch(self, i_switch: 'Switch') -> 'Validator':
        if not i_switch.name or not i_switch.active_value or i_switch.parent_variant().active_state == Tristate.UnknownState:
            return self

        if i_switch.type_ == VariantType.Visibility:
            if i_switch.active_value == Tristate.OnState:
                self._to_show.append(f"Name='{i_switch.name}'")
            else:
                self._to_hide.append(f"Name='{i_switch.name}'")
        elif i_switch.type_ == VariantType.CodeState:
            i_switch.parent_variant().parent.get_variant(
                i_switch.name, 
                lambda v: self._update_variant_state(v, i_switch)
            )
        elif i_switch.type_ == VariantType.Look and i_switch.name != i_switch.active_value:
            if i_switch.active_value.startswith("v_"):
                self.application.look.add_look(i_switch)

        self.deactivate_different(i_switch.parent_variant())
        self.activate_same(i_switch.parent_variant()).deactivate_parents(i_switch.parent_variant())

        return self

    def _update_variant_state(self, v:'Variant', i_switch:'Switch'):
        v.active_state = i_switch.active_value
        self._validate(v)

    def validate_switch(self, i_switch: 'Switch') -> 'Validator':
        self._init_validation()
        self._validate_switch(i_switch)
        self.apply_overrides()
        self.perform_visibility_actions()
        self._finalize_validation()
        return self

    def __del__(self):
        self._to_show = None
        self._to_hide = None
