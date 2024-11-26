
from application.tristate import Tristate
from application.variant_type import VariantType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from application.switch import Switch
    from application.variant import Variant
    
class FlatVariant:
    def __init__(self, iVariant, iState:Tristate=None):
        self.flatten_ok = True
        self._flat_variant = {}

        if iState is not None:
            self._flatten_variant(iVariant, iState)
        else:
            self._flatten_variant(iVariant)

    def _flatten_variant(self, iVariant:'Variant', iState=None):
        if not self.flatten_ok:
            return self

        def add_switch(s:'Switch'):
            if not self.flatten_ok:
                return

            if s.type_ == VariantType.CodeState:
                v = iVariant.parent.get_variant(s.name)
                if v is None:
                    self.flatten_ok = False
                    return

                if iState:
                    self._flatten_variant(v, s.active_value)
                elif v.desired_state == s.active_value:
                    self._flatten_variant(v)
                else:
                    self.flatten_ok = False
            else:
                if s.name in self._flat_variant:
                    if self._flat_variant[s.name] != s.active_value:
                        self.flatten_ok = False
                else:
                    self._flat_variant[s.name] = s.active_value

        if iState:
            iVariant.sub_variants.get_sub_variant(iState, lambda sv: [add_switch(s) for s in sv.switches])
        else:
            [add_switch(s) for s in iVariant.desired_switches]

        return self

    def ready(self, cb, cb_fail=None):
        if self.flatten_ok:
            cb(self)
        elif cb_fail:
            cb_fail()
        return self

    def for_each(self, cb):
        if self.flatten_ok:
            for key, value in self._flat_variant.items():
                cb(key, value)

    def contains(self, iName, cb, cb_fail=None):
        if self.flatten_ok:
            if iName in self._flat_variant:
                cb(self._flat_variant[iName])
            elif cb_fail:
                cb_fail()

    def count(self):
        return len(self._flat_variant)

    def __eq__(self, other:'FlatVariant'):
        if self.count() > other.count():
            return False

        result = True

        def compare(iName, iValue):
            nonlocal result
            if result is False:
                return
            other.contains(iName, lambda val: result if iValue == val else False, lambda: result == False)

        self.for_each(compare)

        return result

    def __ne__(self, other):
        return not self == other

    def is_overlapping(self, iTrg:'FlatVariant'):
        overlapping = False

        def check_overlap(rName, _):
            nonlocal overlapping
            if overlapping:
                return
            if iTrg.contains(rName, lambda _: overlapping == True):
                overlapping = True

        self.for_each(check_overlap)

        return overlapping

    def __del__(self):
        self._flat_variant.clear()
