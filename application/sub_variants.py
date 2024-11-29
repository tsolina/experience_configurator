from typing import TYPE_CHECKING, Callable, Optional, Union, overload
from application.tristate import Tristate
from application.observable_list import ObservableList

if TYPE_CHECKING:
    from application.variant import Variant
    from application.sub_variant import SubVariant


class SubVariants(ObservableList['SubVariant']):
    def __init__(self, parent: 'Variant'):
        super().__init__()
        self._parent = parent
        self.application = parent.application
        self._name = self.__class__.__name__
        # self._active_sub_variant: Optional['SubVariant'] = None
        # self._editing_sub_variant: Optional['SubVariant'] = None
        self._on_variant: Optional['SubVariant'] = None
        self._off_variant: Optional['SubVariant'] = None

        # Initialize SubVariants based on Tristate states
        from application.sub_variant import SubVariant
        for state_name in Tristate.to_list():
            self.append(SubVariant(self, state_name))

        # self.active_sub_variant = self[0]
        # print(self.__class__.__name__, "init", self.active_sub_variant, self.active_sub_variant is None)
        # self.editing_sub_variant = self.active_sub_variant

    @property
    def parent(self) -> 'Variant':
        return self._parent

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    # @property
    # def active_sub_variant(self) -> Optional['SubVariant']:
    #     return self._active_sub_variant

    # @active_sub_variant.setter
    # def active_sub_variant(self, value: 'SubVariant'):
    #     self._active_sub_variant = value

    #     self.application.context.view_variant_editor_event_handler.update_sub_variant_container(self)

    # @property
    # def editing_sub_variant(self) -> Optional['SubVariant']:
    #     return self._editing_sub_variant

    # @editing_sub_variant.setter
    # def editing_sub_variant(self, value: 'SubVariant'):
    #     self._editing_sub_variant = value

    @property
    def on_variant(self) -> 'SubVariant':
        if self._on_variant is None:
            self._on_variant = self.get_sub_variant(Tristate.OnState)
        return self._on_variant

    @property
    def off_variant(self) -> 'SubVariant':
        if self._off_variant is None:
            self._off_variant = self.get_sub_variant(Tristate.OffState)
        return self._off_variant

    # def get_sub_variant(self, name: str) -> Optional['SubVariant']:
    #     return next((sv for sv in self if sv.name == name), None)

    # def get_sub_variant_with_callback(self, name: str, callback: Callable[['SubVariant'], None]):
    #     sub_variant = self.get_sub_variant(name)
    #     if sub_variant is not None:
    #         callback(sub_variant)
    #     else:
    #         self.application.error_message = f"State {name} of variant {self.parent.name} not found"

    @overload
    def get_sub_variant(self, name: str) -> Optional['SubVariant']: ...
    
    @overload
    def get_sub_variant(self, name: str, callback: Callable[['SubVariant'], None]) -> None: ...

    def get_sub_variant(self, name: str, callback: Optional[Callable[['SubVariant'], None]] = None) -> Union[Optional['SubVariant'], None]:
        """
        Retrieves a sub-variant by name, optionally invoking a callback.

        Args:
            name (str): The name of the sub-variant to retrieve.
            callback (Optional[Callable[[CSubVariant], None]]): A callback to invoke with the sub-variant if found.

        Returns:
            Optional[CSubVariant]: The found sub-variant, or None if no callback is provided and the sub-variant isn't found.
        """
        sub_variant = next((sv for sv in self if sv.name == name), None)

        def handle_error() -> None:
            """
            Internal function to handle the error when a sub-variant is not found.
            """
            error_message = f"State '{name}' of variant '{self.parent.name}' not found"
            print(error_message)  # Replace with actual error handling logic.

        if callback:
            if sub_variant:
                callback(sub_variant)
            else:
                handle_error()
        else:
            return sub_variant

    def for_each(self, callback: Callable[['SubVariant'], None]):
        for sub_variant in self:
            callback(sub_variant)

    def __del__(self):
        self.clear()
