from typing import TYPE_CHECKING
from application.actor_catia import ActorCatia
from application.eval_selected import EvalSelected
import experience as exp
import tkinter as tk

if TYPE_CHECKING:
    from .actors import Actors

class Actor:
    def __init__(self, parent: 'Actors', id="", name="", type_="", cat_object: exp.AnyObject=None, path="", link_on_feature: exp.AnyObject=None, err_message=""):
        self.application = parent.application
        self._uID = self.application.guid
        self._parent = parent
        self.link_on_feature = link_on_feature
        self._name = name if name else self.__class__.__name__
        self._id = id
        self._type = type_
        self._cat_object = cat_object
        self._path = path
        self._err_message = err_message
        self.evaluated:EvalSelected = None

        if cat_object:
            self.evaluated = EvalSelected(self.application, self.cat_object)

        self.name_var = tk.StringVar(value=self._name)
        self.type_var = tk.StringVar(value=self._type)
        self.error_message_var = tk.StringVar(value=self._err_message)
        

        self.name_var.trace_add("write", self._update_name_from_var)
        self.type_var.trace_add("write", self._update_type_from_var)
        self.error_message_var.trace_add("write", self._update_error_message_from_var)

    def _update_name_from_var(self, *args):
        # Synchronize name with name_var
        self.name = self.name_var.get()

    def _update_type_from_var(self, *args):
        # Synchronize name with name_var
        self.type_ = self.type_var.get()

    def _update_error_message_from_var(self, *args):
        # Synchronize name with name_var
        self.err_message = self.error_message_var.get()

    @property
    def parent(self) -> 'Actors':
        return self._parent

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value
        # self.raise_property_changed("Name")

    @property
    def uID(self) -> int:
        return self._uID

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str):
        self._id = value
        # self.raise_property_changed("Id")

    @property
    def type_(self) -> str:
        return self._type

    @type_.setter
    def type_(self, value: str):
        self._type = value
        # self.raise_property_changed("Type")

    @property
    def cat_object(self) -> exp.AnyObject:
        return self._cat_object

    @cat_object.setter
    def cat_object(self, value):
        self._cat_object = value
        self.evaluated = EvalSelected(self.application, self.cat_object)
        # self.raise_property_changed("CatObject")

    @property
    def com_id(self) -> str:
        if self.cat_object is None:
            return None
        
        return self.evaluated.path

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: str):
        self._path = value
        # self.raise_property_changed("Path")

    @property
    def err_message(self) -> str:
        return self._err_message

    @err_message.setter
    def err_message(self, value: str):
        self._err_message = value
        self.parent.parent.err_message = "E"  # Assuming `parent` and `parent.parent` are valid
        # self.raise_property_changed("ErrMessage")

    def to_actor_catia(self):
        return ActorCatia(
            cat_object=self.cat_object,
            link_on_feature=self.link_on_feature,
            path=self.path,
            type_=self.type_
        )
    
    def __del__(self):
        # Simulating Finalize behavior
        self.link_on_feature = None
        self._cat_object = None
        # print(f"Cleaned up {self.__class__.__name__} object")