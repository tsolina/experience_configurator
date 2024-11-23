from typing import Optional, Any, TYPE_CHECKING, Union, overload
from application.tristate import Tristate
import experience as exp

if TYPE_CHECKING:
    from application.actor import Actor
    from application.application import Application
    from application.configuration import Configuration

class LookValidator:
    def __init__(self, parent: 'Application'):
        self._parent: Application = parent  # Simulates the parent object
        self.application = parent
        self._name: str = self.__class__.__name__

    @property
    def parent(self) -> 'Application':
        return self._parent

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @overload
    def validate(self, i_actor: 'Actor') -> 'LookValidator':
        ...

    @overload
    def validate(self, i_config: 'Configuration') -> 'LookValidator':
        ...

    @overload
    def validate(self, i_config: 'Configuration', i_apply: bool) -> 'LookValidator':
        ...  

    def validate(self, arg: Union['Actor', 'Configuration'], i_apply: bool = True) -> 'LookValidator':
        """
        Unified implementation of the overloaded methods.
        Calls the appropriate logic based on the type of the argument.
        """
        from application.actor import Actor
        from application.configuration import Configuration
        if isinstance(arg, Actor):
            return self._validate_actor(arg)
        elif isinstance(arg, Configuration):
            return self._validate_configuration(arg, i_apply)
        else:
            raise TypeError(f"Invalid argument type: {type(arg).__name__}")

    def _validate_actor(self, i_actor: 'Actor') -> 'LookValidator':
        if i_actor.cat_object is None:
            return self

        # Recursive validation of the parent configuration
        self.validate(i_actor.parent.parent)

        if i_actor.parent.parent.active_look_state == Tristate.OnState:
            if i_actor.parent.parent.active_look != "":
                self.application.look.add_look(i_actor)
                self.deactivate_different(i_actor.parent.parent)

        return self
    
    def _validate_configuration(self, i_config: 'Configuration', i_apply: bool) -> 'LookValidator':
        if i_config.active_look_state == Tristate.OnState:
            self.deactivate_different(i_config)
            # i_config.active_look_state = Tristate.OnState  # Redundant but matches VB.NET
            i_config.active_look_state_var.set(Tristate.OnState)

            if i_apply:
                self.apply_look(i_config)

        return self


    def invalidate(self, actor: 'Actor') -> 'LookValidator':
        if actor.cat_object is None:
            return self
        
        if actor.parent.parent.active_look_state == Tristate.OnState:
            if actor.parent.parent.active_look != "":
                self.application.look.remove_look(actor)
                self.deactivate_different(actor.parent.parent)

        return self

    def config_overlapping(self, reference: 'Configuration', target: 'Configuration') -> bool:
        overlapping = False
        # print(self.__class__.__name__, "config_overlapping")
        if reference.actors.count == 0 and target.actors.count == 0:
            overlapping = True

        for ref_actor in reference.actors.actor_list:
            if overlapping:
                break
            for target_actor in target.actors.actor_list:
                if overlapping:
                    break
                # print(self.__class__.__name__, "config_overlapping", ref_actor.cat_object is target_actor.cat_object, ref_actor.com_id == target_actor.com_id, ref_actor.com_id, target_actor.com_id)
                # if ref_actor.cat_object is target_actor.cat_object:
                if ref_actor.com_id == target_actor.com_id:
                    overlapping = True
                    break

        return overlapping

    def config_differs(self, reference: 'Configuration', target: 'Configuration') -> bool:
        differs = False
        if reference.actors.count == 0 and target.actors.count == 0:
            return False

        for ref_actor in reference.actors.actor_list:
            if differs:
                break
            target_actor = next((a for a in target.actors.actor_list if a.com_id == ref_actor.com_id), None)
            if target_actor is None:
                differs = True
                break

        return differs

    def deactivate_different(self, config: 'Configuration') -> 'LookValidator':
        for conf in config.parent.configuration_collection:
            if conf.uID == config.uID or conf.active_look_state == Tristate.OffState:
                continue
            
            # print(self.__class__.__name__, "deactivate different", "overlapping?")
            if self.config_overlapping(config, conf):
                # print(self.__class__.__name__, "deactivate different", "overlapping", config.name, conf.name)
                if conf.actors.count != config.actors.count:
                    conf.active_look_state_var.set(Tristate.OffState)
                    continue
            else:
                continue

            print(self.__class__.__name__, "deactivate different", "differs?")
            if self.config_differs(config, conf):
                print(self.__class__.__name__, "deactivate different", "differs", config.name, conf.name)
                conf.active_look_state_var.set(Tristate.OffState)
            else:
                if conf.active_look != config.active_look:
                    conf.active_look_state_var.set(Tristate.OffState)

        return self

    def apply_look(self, config: 'Configuration') -> 'LookValidator':
        if config.active_look == "" or config.active_look not in config.look_collection:
            return self

        for actor in config.actors.actor_list:
            self.application.look.add_look(actor)

        return self

    def validate_config(self, config: 'Configuration', apply: bool = True) -> 'LookValidator':
        if config.active_look_state == Tristate.OnState:
            self.deactivate_different(config)
            # config.active_look_state = Tristate.OnState
            config.active_look_state_var.set(Tristate.OnState)

            if apply:
                self.apply_look(config)

        return self
