from typing import TYPE_CHECKING
from application.tristate import Tristate
from application.variant import Variant

if TYPE_CHECKING:
    from application.sub_variant import SubVariant

class SubVariants():
    def __init__(self, parent: 'Variant'):
        self._parent = parent
        self.application = parent.application
        self._name = self.__class__.__name__
        self._sub_variant_collection = [SubVariant]
        self._active_sub_variant = None
        self._editing_sub_variant = None
        self._on_variant = None
        self._off_variant = None

        # Initialize SubVariants based on MTristate states
        for name in Tristate.to_list():
            from application.sub_variant import SubVariant
            self._sub_variant_collection.append(SubVariant(self, name))

        self.active_sub_variant = self._sub_variant_collection[0]
        self.editing_sub_variant = self.active_sub_variant

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
    def active_sub_variant(self) -> 'SubVariant':
        return self._active_sub_variant

    @active_sub_variant.setter
    def active_sub_variant(self, value:'SubVariant'):
        self._active_sub_variant = value

    @property
    def editing_sub_variant(self) -> 'SubVariant':
        return self._editing_sub_variant

    @editing_sub_variant.setter
    def editing_sub_variant(self, value:'SubVariant'):
        self._editing_sub_variant = value

    @property
    def sub_variant_collection(self) ->list['SubVariant']:
        return self._sub_variant_collection

    @sub_variant_collection.setter
    def sub_variant_collection(self, value:list['SubVariant']):
        self._sub_variant_collection = value

    @property
    def on_variant(self):
        if self._on_variant is None:
            self._on_variant = self.get_sub_variant(Tristate.OnState)
        return self._on_variant

    @property
    def off_variant(self):
        if self._off_variant is None:
            self._off_variant = self.get_sub_variant(Tristate.OffState)
        return self._off_variant

    def get_sub_variant(self, iName) -> 'SubVariant':
        return next((sv for sv in self._sub_variant_collection if sv.name == iName), None)

    def get_sub_variant_with_callback(self, iName, cb):
        sv = self.get_sub_variant(iName)
        if sv is not None:
            cb(sv)
        else:
            self.application.error_message = f"State {iName} of variant {self._parent.name} not found"

    def for_each(self, cb):
        for sv in self._sub_variant_collection:
            cb(sv)

    def __del__(self):
        self._sub_variant_collection.clear()
        self._sub_variant_collection = None
