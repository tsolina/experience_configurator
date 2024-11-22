from typing import Optional

from application.actor_catia import ActorCatia
import experience as exp

class LookObject:
    def __init__(self, actor: Optional['ActorCatia'] = None, look_active:str="", target_name:str="", desired_look:str="", 
                 material_applied: Optional[exp.AppliedMaterial] = None, target_override: str = ""):
        self._actor = actor
        self._look_active = look_active
        self._target_name = target_name
        self._desired_look = desired_look
        self._material_applied = material_applied
        self._target_override = target_override

    @property
    def actor(self) -> Optional['ActorCatia']:
        return self._actor

    @actor.setter
    def actor(self, value: 'ActorCatia') -> None:
        self._actor = value

    @property
    def look_active(self) -> str:
        return self._look_active

    @look_active.setter
    def look_active(self, value: str) -> None:
        self._look_active = value

    @property
    def target_name(self) -> str:
        return self._target_name

    @target_name.setter
    def target_name(self, value: str) -> None:
        self._target_name = value

    @property
    def desired_look(self) -> str:
        return self._desired_look

    @desired_look.setter
    def desired_look(self, value: str) -> None:
        self._desired_look = value

    @property
    def material_applied(self) -> Optional[exp.AppliedMaterial]:
        return self._material_applied

    @material_applied.setter
    def material_applied(self, value: exp.AppliedMaterial) -> None:
        self._material_applied = value

    @property
    def target_override(self) -> str:
        return self._target_override

    @target_override.setter
    def target_override(self, value: str) -> None:
        self._target_override = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LookObject):
            return NotImplemented
        return self.actor.path == other.actor.path if self.actor and other.actor else False

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, LookObject):
            return NotImplemented
        return self.actor.path != other.actor.path if self.actor and other.actor else False

    def __del__(self):
        # Cleanup on deletion
        self._actor = None
        self._material_applied = None

    def deep_copy(self) -> 'LookObject':
        return LookObject(
            actor=self.actor,
            look_active=self.look_active,
            target_name=self.target_name,
            desired_look=self.desired_look,
            material_applied=self.material_applied
        )
