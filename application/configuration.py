from typing import TYPE_CHECKING, List

from application.look_container import LookContainer
from application.tristate import Tristate
import tkinter as tk



if TYPE_CHECKING:
    from application.actors import Actors
    from application.actor import Actor
    from application.configurations import Configurations


class Configuration:
    def __init__(self, parent: 'Configurations', id:int=None, name:str=None, look_states:List[str]=[], active_state:str="", active_look:str=""):
        self._parent = parent
        self.application = parent.application
        self._uID = self.application.guid       
        self._name = name or self.__class__.__name__
        self._id = id
        self._look_states: List[str] = look_states
        self._active_look_state = active_state
        self._look_collection:List[str] = []
        self._active_look = active_look
        self._actors:'Actors' = None
        self._init_helper()
        self._active_actor = None
        self._err_message = ""
        self.property_true_value_selection = False
        self._rttUID = ""

        self.active_look_var = tk.StringVar(value=self._active_look)
        self.active_look_state_var = tk.StringVar(value=self._active_look_state)
        self.name_var = tk.StringVar(value=self._name)

        self.name_var.trace_add("write", self._update_name_from_var)
        self.active_look_var.trace_add("write", self._update_active_look_from_var)
        self.active_look_state_var.trace_add("write", self._update_active_look_state_from_var)


    def _init_helper(self):
        from application.actors import Actors
        self._actors = Actors(self)

        def set_look_coolection(look_container:'LookContainer'):
            self._look_collection = look_container.targets_list
        self.application.look_file.ready(set_look_coolection)

    @property
    def parent(self) -> 'Configurations':
        return self._parent

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def uID(self) -> int:
        return self._uID

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str):
        self._id = value

    @property
    def look_states(self) -> list:
        return self._look_states

    @look_states.setter
    def look_states(self, value: list[str]):
        self._look_states = value

    @property
    def active_look_state(self) -> str:
        return self._active_look_state

    @active_look_state.setter
    def active_look_state(self, value: str):
        self._active_look_state = value
        # print(self.__class__.__name__, "active_look_state", self.name, "on", self.property_true_value_selection)
        if self.property_true_value_selection:
            self.property_true_value_selection = False
            self.application.look_validator.validate(self)   
        # print(self.__class__.__name__, "active_look_state", self.name, "check", self.active_look_state)         

    @property
    def look_collection(self) -> list:
        return self._look_collection

    @look_collection.setter
    def look_collection(self, value: list):
        self._look_collection = value

    @property
    def active_look(self) -> str:
        return self._active_look

    @active_look.setter
    def active_look(self, value: str):
        self._active_look = value
        if self.property_true_value_selection:
            self.property_true_value_selection = False
            self.application.look_validator.validate(self) 

    def __eq__(self, other: 'Configuration') -> bool:
        return isinstance(other, Configuration) and self.uID == other.uID

    def __ne__(self, other: 'Configuration') -> bool:
        return not self.__eq__(other)
    
    @property
    def actors(self) -> 'Actors':
        return self._actors

    @actors.setter
    def actors(self, value: 'Actors'):
        self._actors = value

    @property
    def active_actor(self) -> 'Actor':
        return self._active_actor

    @active_actor.setter
    def active_actor(self, value: 'Actor'):
        self._active_actor = value

    @property
    def err_message(self) -> str:
        return self._err_message

    @err_message.setter
    def err_message(self, value: str):
        self._err_message = value

    def toggle(self) -> 'Configuration':
        self.property_true_value_selection = True

        if self.active_look_state == self.look_states[0]:
            self.active_look_state = self.look_states[-1]
        else:
            self.active_look_state = self.look_states[0]

        self.parent.parent.active_configuration = self
        self.property_true_value_selection = False

        return self
    
    @property
    def rttUID(self) -> str:
        if not self._rttUID:
            my_id = f"{self.uID:04d}"
            self._rttUID = f"{{12345678-{my_id}-5678-5678-123456789abc}}"
        return self._rttUID
    
    def _update_active_look_from_var(self, *args):
        # Synchronize active_look with active_look_var
        self.property_true_value_selection = True
        self.active_look = self.active_look_var.get()

    def _update_active_look_state_from_var(self, *args):
        # Synchronize active_look_state with active_look_state_var
        self.property_true_value_selection = True
        self.active_look_state = self.active_look_state_var.get()
        # print(self.__class__.__name__, "update_active_look_state_from_var", self.name)

    def _update_name_from_var(self, *args):
        # Synchronize name with name_var
        self.active_look_state = self.name_var.get()

    
    def __del__(self):
        # Finalization equivalent
        self._look_states = None
        self._look_collection = None