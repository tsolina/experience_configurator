from application.tristate import Tristate
from application.variant_type import VariantType
from typing import TYPE_CHECKING, Callable, Dict, Optional, TypeVar, overload

T = TypeVar('T', bound='FlatVariant')

if TYPE_CHECKING:
    from application.switch import Switch
    from application.variant import Variant
    
class FlatVariant:
    def __init__(self, variant:'Variant', iState:Tristate=None):
        self.flatten_ok = True
        self._flat_variant: Dict[str, str] = {}

        if iState is not None:
            self.flatten_variant(variant, iState)
        else:
            self.flatten_variant(variant)

    @overload
    def ready(self, cb: Callable[[T], None]) -> T: ...
    
    @overload
    def ready(self, cb: Callable[[T], None], cb_fail: Callable[[], None]) -> T: ...

    def ready(self, cb: Callable[[T], None], cb_fail: Optional[Callable[[], None]] = None) -> T:
        """
        Executes the callback if flattening is OK, otherwise executes the failure callback if provided.

        Args:
            cb (Callable[[FlatVariant], None]): Callback to invoke if flattening is OK.
            cb_fail (Optional[Callable[[], None]]): Callback to invoke if flattening fails.

        Returns:
            FlatVariant: The current instance.
        """
        if self.flatten_ok:
            cb(self)  # Pass the current instance to the callback.
        elif cb_fail:
            cb_fail()  # Invoke the failure callback if provided.

        return self
    
    @overload
    def flatten_variant(self, variant: 'Variant') -> T: ...
    
    @overload
    def flatten_variant(self, variant: 'Variant', state: str) -> T: ...

    def flatten_variant(self, variant: 'Variant', state: Optional[str] = None) -> T:
        """
        Flattens a variant into the current flat variant dictionary.

        Args:
            variant (CVariant): The variant to flatten.
            state (Optional[str]): The optional state to use when flattening.

        Returns:
            FlatVariant: The current instance.
        """
        if not self.flatten_ok:
            return self

        def process_switch(switch: 'Switch') -> None:
            nonlocal variant
            if not self.flatten_ok:
                return

            if switch.type_ == VariantType.CodeState:
                sub_variant = variant.parent.get_variant(switch.name)
                if not sub_variant:
                    self.flatten_ok = False
                    return

                if state and sub_variant.desired_state == state:
                    self.flatten_variant(sub_variant, switch.active_value)
                elif not state:
                    self.flatten_variant(sub_variant)
                else:
                    self.flatten_ok = False
            else:
                if switch.name in self._flat_variant:
                    if self._flat_variant[switch.name] != switch.active_value:
                        self.flatten_ok = False
                        return
                else:
                    self._flat_variant[switch.name] = switch.active_value

        if state:
            # variant.sub_variants.get_sub_variant(state, lambda sv: [process_switch(s) for s in sv.desired_switches])
            variant.sub_variants.get_sub_variant(state, lambda sv: [process_switch(s) for s in sv.switches])
        else:
            for switch in variant.desired_switches:
                process_switch(switch)

        return self
    

    def for_each(self, callback: Callable[[str, str], None]) -> None:
        """
        Iterates over the flat variant dictionary and invokes the callback for each key-value pair.

        Args:
            callback (Callable[[str, str], None]): A function to invoke with each key-value pair.
        """
        def _execute_callback(context:'FlatVariant') -> None:
            """
            Internal function to iterate through the flat variant and execute the callback.
            """
            for key, value in context._flat_variant.items():
                callback(key, value)

        self.ready(_execute_callback)

    @overload
    def contains(self, name: str) -> bool:
        """Checks if the key exists and returns a boolean result."""
        ...

    @overload
    def contains(self, name: str, callback: Callable[[str], None]) -> None:
        """Checks if the key exists and invokes a callback if true."""
        ...

    @overload
    def contains(
        self, 
        name: str, 
        callback: Callable[[str], None], 
        fail_callback: Callable[[], None]
    ) -> None:
        """Checks if the key exists and invokes either a success or failure callback."""
        ...

    def contains(
        self, 
        name: str, 
        callback: Optional[Callable[[str], None]] = None, 
        fail_callback: Optional[Callable[[], None]] = None
    ) -> Optional[bool]:
        """
        Checks if a key exists in the flat variant dictionary.

        Args:
            name (str): The key to check.
            callback (Optional[Callable[[str], None]]): A function to invoke if the key exists, receiving the associated value.
            fail_callback (Optional[Callable[[], None]]): A function to invoke if the key does not exist.

        Returns:
            Optional[bool]: `True` if the key exists, `False` if not, or `None` if callbacks are provided.
        """
        def _execute_logic(context:FlatVariant) -> None:
            """
            Internal function to execute the contains logic based on callbacks.
            """
            if name in context._flat_variant:
                if callback:
                    callback(context._flat_variant[name])
            else:
                if fail_callback:
                    fail_callback()

        if callback or fail_callback:
            self.ready(_execute_logic)
        else:
            return name in self._flat_variant
        


    def count(self):
        return len(self._flat_variant)
    
    def __eq__(self, other: "FlatVariant") -> bool:
        """Equality operator implementation."""
        if not isinstance(other, FlatVariant):
            return NotImplemented

        if len(self._flat_variant) > len(other._flat_variant):
            return False

        result = True

        def check_key_value(name: str, value: str) -> None:
            nonlocal result
            if not result:
                return  # Exit early if already determined false

            def success_callback(val: str) -> None:
                nonlocal result
                result = (value == val)

            def fail_callback() -> None:
                nonlocal result
                result = False

            other.contains(name, success_callback, fail_callback)

        self.ready(lambda context: [check_key_value(name, value) for name, value in context._flat_variant.items()])
        return result

    def __ne__(self, other):
        return not self == other
    
    def is_overlapping(self, target: "FlatVariant") -> bool:
        """
        Determines if there is any overlap between this CFlatVariant and the target CFlatVariant.
        
        Args:
            target (CFlatVariant): The target variant to check for overlapping keys.

        Returns:
            bool: True if there is any overlapping key, False otherwise.
        """
        result = False

        def check_overlap(name: str, value: str) -> None:
            nonlocal result
            if result:
                return  # Exit early if overlap is already found

            if target.contains(name):
                result = True

        self.for_each(check_overlap)
        return result


    def __del__(self):
        self._flat_variant.clear()
