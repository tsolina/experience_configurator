from typing import Union, overload, TYPE_CHECKING
from application.actor import Actor

from application.look_container import LookContainer
from application.look_object import LookObject
from application.look_override import LookOverride
from application.switch import Switch
from application.tristate import Tristate
import experience as exp

if TYPE_CHECKING:
    from application.application import Application
    
class Look():
    NO_LOOK = "No Look"

    def __init__(self, parent: 'Application'):
        self._parent = parent  # Equivalent of CModel in the VB.NET code
        self.application: 'Application' = parent
        self.trg_part: exp.Part = None  # MECMOD.Part
        self._actor: 'Actor' = None  # CActorCatia
        self._look: 'LookObject' = None  # CLookObject
        self.look_overrides = [LookOverride]

        self._name = self.__class__.__name__

    @property
    def parent(self):
        return self._parent

    @property
    def i_parent(self):
        return self._parent

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def get_part_from_object(self, obj:exp.AnyObject) -> exp.Part:
        obj_type = obj.com_type()

        if obj_type == "Part":
            return obj
        elif obj_type == "VPMRootOccurrence":
            return None
        # elif obj_type == type(obj.parent).__name__:
        elif obj_type == obj.parent().com_type():
            if obj_type == "OrderedGeometricalSets" or obj_type == "ParmsSet":
                return self.get_part_from_object(obj.parent())
            return None
        return self.get_part_from_object(obj.parent())

    def set_trg_link_on_feature(self):
        if self._actor.link_on_feature is not None:
            return

        if self._actor.type_ == "Container":
            try:
                self._actor.link_on_feature = self.application.catia.services().product_service().compose_link(self._actor.cat_object, None, None)
            except Exception as e:
                print(f"Err: link on feature failed {self._actor.path}")
        elif self._actor.type_ == "VPMReference":
            vpm_ref: exp.VPMReference = self._actor.cat_object
            if vpm_ref.rep_instances():
                rep_instance = vpm_ref.rep_instances().item(1)
                self._actor.link_on_feature = self.application.catia.services().product_service().compose_link(None, rep_instance, None)
            else:
                self._actor.link_on_feature = self.application.catia.services().product_service().compose_link(None, None, self._actor.cat_object)
        elif self._actor.type_ == "VPMRepReference":
            self._actor.link_on_feature = self.application.catia.services().product_service().compose_link(None, self._actor.cat_object, None)
        else:
            try:
                no_occurrence = None
                vpm_ref = self.trg_part.parent().father()
                rep_instance = vpm_ref.rep_instances().item(1)
                self._actor.link_on_feature = self.application.catia.services().product_service().compose_link(no_occurrence, rep_instance, self.trg_part.create_reference_from_object(self._actor.cat_object))
            except Exception as e:
                self._actor.link_on_feature = self.application.catia.services().product_service().compose_link(
                    None, self.trg_part.parent().parent().item(1), self.trg_part.create_reference_from_object(self._actor.cat_object))

    def is_look_necessary(self):
        if self._look.desired_look == self._look.look_active:
            return False
        if self._look.desired_look.startswith("t_") and self._look.look_active.startswith("v_"):
            return False
        return True

    def is_trg_part_ok(self):
        if self._actor.type_ in ["Container", "VPMReference"]:
            return True

        self.trg_part = self.get_part_from_object(self._actor.cat_object)
        if self.trg_part is None:
            self.application.status_message = f"Element invalid, material cannot be added, {self._actor.path}"
            return False
        return True

    def remove_any_look(self):
        self.set_trg_link_on_feature()

        covering_applied_materials: exp.AppliedMaterials = None
        try:
            col, covering_applied_materials = self.application.catia.services().mat_plm_service().get_material_covering(self._actor.link_on_feature)
        except Exception:
            return

        if covering_applied_materials is None or covering_applied_materials.count() == 0:
            return

        try:
            self.application.catia.services().mat_plm_service().remove_applied_material(covering_applied_materials.item(1))
        except Exception:
            print(f"Error: Cannot remove material {self._actor.path}")
        # for i in range(1, covering_applied_materials.count() + 1):
        #     self.application.catia.services().mat_plm_service().remove_applied_material(covering_applied_materials.item(1))
        self._look.look_active = ""
    
    @overload
    def remove_look(self) -> 'Look':
        ...

    @overload
    def remove_look(self, look_object: 'LookObject') -> 'Look':
        ...

    @overload
    def remove_look(self, actor: 'Actor') -> 'Look':
        ...

    def remove_look(self, arg: Union[None, 'LookObject', 'Actor'] = None) -> 'Look':
        """
        Unified remove_look method handling multiple types of input.
        """
        if arg is None:
            return self._remove_look_default()
        elif isinstance(arg, LookObject):
            return self._remove_look_from_look_object(arg)
        elif isinstance(arg, Actor):
            return self._remove_look_from_actor(arg)
        else:
            raise TypeError(f"Invalid argument type: {type(arg).__name__}")
        
    def _remove_look_default(self) -> 'Look':
        if self._look and self._look.material_applied:
            try:
                self.application.catia.services().mat_plm_service().remove_applied_material(self._look.material_applied)
                self._look.look_active = ""
            except Exception:
                self.remove_any_look()
            return self

        self.remove_any_look()
        return self

    def _remove_look_from_look_object(self, look_object: 'LookObject') -> 'Look':
        self._look = look_object
        self._actor = self._look.actor
        if not self.is_trg_part_ok():
            return self

        self._remove_look_default()
        self._look.target_name = self.NO_LOOK
        return self

    def _remove_look_from_actor(self, actor: 'Actor') -> 'Look':
        def look_ready(look_container:'LookContainer'):
            look_object = None
            if self.application.active_project.look_actors.get(actor.path):
                look_object = self.application.active_project.look_actors[actor.path]
                look_object.desired_look = self.NO_LOOK
            else:
                look_object = LookObject(
                    actor.to_actor_catia(),
                    desired_look=self.NO_LOOK,
                    target_name=self.NO_LOOK
                )
                self.application.active_project.look_actors[actor.path] = look_object

            self.remove_look(look_object)

        self.application.project_ready(lambda p: self.application.look_file.ready(look_ready))
        return self
    

    def attach_look(self):
        if self._look.desired_look in [self.NO_LOOK, ""]:
            return self
        if self._actor.cat_object is None:
            print(f"{self._actor.path} object is None")
            return self

        def apply_material(look_container:'LookContainer'):
            material_generic = None
            if self._look.desired_look.startswith("t_"):
                material_generic = self.application.look_file.targets_dict[self._look.desired_look]
                self._look.target_name = self._look.desired_look
            else:
                material_generic = self.application.look_file.variants_dict[self._look.desired_look]

            try:
                self._look.material_applied = self.application.catia.services().mat_plm_service().set_material_covering(self._actor.link_on_feature, material_generic)
                self._look.look_active = self._look.desired_look
            except Exception:
                print(f"Error: Cannot attach look on {self._actor.path}", Exception)


        self.application.look_file.ready(apply_material)
        return self
    
    @overload
    def add_look(self, look_object: 'LookObject') -> 'Look':
        ...

    @overload
    def add_look(self, switch: 'Switch') -> 'Look':
        ...

    @overload
    def add_look(self, actor: 'Actor') -> 'Look':
        ...

    def add_look(self, arg: Union['LookObject', 'Switch', 'Actor']) -> 'Look':
        """
        Unified add_look method handling multiple types of input.
        """
        if isinstance(arg, LookObject):
            return self._add_look_from_look_object(arg)
        elif isinstance(arg, Switch):
            return self._add_look_from_switch(arg)
        elif isinstance(arg, Actor):
            return self._add_look_from_actor(arg)
        else:
            raise TypeError(f"Invalid argument type: {type(arg).__name__}")
        
    def _add_look_from_look_object(self, look_object: 'LookObject') -> 'Look':
        self._look = look_object
        if not self.is_look_necessary():
            return self

        self._actor = self._look.actor
        if not self.is_trg_part_ok():
            return self

        self.remove_look()
        self.attach_look()
        return self

    def _add_look_from_switch(self, switch: 'Switch') -> 'Look':
        def ready_action():
            for name, look_object in self.application.active_project.look_actors.items():
                if look_object.target_override == "" and look_object.target_name == switch.name:
                    look_object.desired_look = switch.active_value
                    self.add_look(look_object)
                elif look_object.target_override == switch.name:
                    look_object.desired_look = switch.active_value
                    self.add_look(look_object)

        self.application.look_file.ready(ready_action)
        return self

    def _add_look_from_actor(self, actor: 'Actor') -> 'Look':
        def look_ready(look_container:'LookContainer'):
            if not actor.path:
                return

            look_object = None
            if actor.path in self.application.active_project.look_actors:
                look_object = self.application.active_project.look_actors[actor.path]
                look_object.desired_look = actor.parent.parent.active_look
                look_object.target_name = look_object.desired_look
            else:
                look_object = LookObject(
                    actor.to_actor_catia(),
                    desired_look=actor.parent.parent.active_look,
                    target_name=actor.parent.parent.active_look
                )
                self.application.active_project.look_actors[actor.path] = look_object

            self.add_look(look_object)

        self.application.project_ready(lambda p: self.application.look_file.ready(look_ready))
        return self

    def apply_look_to_all(self):
        def ready_action():
            for variant in self.application.active_project.variants.variant_collection:
                if variant.active_state == Tristate.OffState:
                    continue
                for switch in variant.active_sub_variant.switches:
                    self.add_look(switch)

        self.application.ready(ready_action)
        self.application.catia.start_command("Apply customized view")
        return self

    def __del__(self):
        self.trg_part = None
        self._actor = None
        self._look = None
        self.look_overrides.clear()
        self.look_overrides = None