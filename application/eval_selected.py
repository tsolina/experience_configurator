import experience as exp
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from application.application import Application

class EvalSelected:
    def __init__(self, application: 'Application', item: exp.AnyObject):
        self.application = application
        self.type_ = ""
        self.name = ""
        self.cat_obj: exp.AnyObject = None
        self.message = ""
        self.path = ""
        self._level = 1
        if item is None:
            self.message = "NotFound"
        else:
            self.eval_selected(item)

    def __del__(self):
        self.cat_obj = None

    def eval_selected(self, item: exp.AnyObject):
        """Dispatch based on item type."""
        item_type = item.com_type() #type(item).__name__

        if item_type == "VPMRootOccurrence":
            self.message = "root object cannot be used"
        elif item_type == "VPMOccurrence":
            self.eval_selected_vpm_occurrence(item)
        elif item_type == "VPMReference":
            self.eval_selected_vpm_reference(item)
        elif item_type == "VPMRepReference":
            self.eval_selected_vpm_rep_reference(item)
        elif item_type == "VPMRepInstance":
            self.eval_selected(item.reference_instance_of())
        elif item_type == "Body":
            self.type_ = "Body"
            self.name = item.name()
            self.cat_obj = item
            self.set_path(item)
        elif item_type == "Shapes":
            self.eval_selected(item.parent())
        elif item_type == "HybridBody":
            self.type_ = "HybridBody"
            self.name = item.name()
            self.cat_obj = item
            self.set_path(item)
        elif item_type == "HybridShapes":
            self.eval_selected(item.parent())
        else:
            self.eval_parent(item)

    def eval_selected_vpm_occurrence(self, item: exp.VPMOccurrence):
        if item is None:
            self.message = "item is nothing"
            return
        try:
            if item.name() is None:
                self.message = "item name is nothing"
                return
        except Exception:
            self.message = "resynchronizing"
            # Reset projects as needed, similar to App.Model.ActiveProject.Occurences.Clear()
            return

        self.type_ = "Container"
        self.name = item.name()
        self.cat_obj = item
        self.set_path(item)

    def eval_selected_vpm_reference(self, item: exp.VPMReference):
        # Recursively call with the occurrence by ID
        self.eval_selected(self.application.active_project.occurrences[item.id].occurrence)

    def eval_selected_vpm_rep_reference(self, item: exp.VPMRepReference):
        try:
            self.eval_selected(item.father())
        except Exception:
            self.message = "Standalone 3dshapes are currently not supported"

    def eval_parent(self, item: exp.AnyObject):
        if self._level > 2:
            return
        parent_type = item.parent().com_type()
        self.type_ = parent_type
        self.message = f"{parent_type}: {item.name()} not supported"
        self._level += 1

        if parent_type == "HybridShapes":
            self.message = ""
            self.eval_selected(item.parent())
        elif parent_type == "Shapes":
            self.message = ""
            self.eval_selected(item.parent())
        elif parent_type == "AxisSystems":
            self.eval_selected(item.parent())
        elif parent_type == "Part":
            self.eval_selected(item.parent())
        elif parent_type == "HybridShapeSurfaceExplicit":
            self.message = ""
            self.eval_selected(item.parent())
        else:
            self.eval_parent(item.parent())

    def set_path(self, entity: exp.AnyObject):
        entity_type = entity.com_type() #type(entity).__name__

        if entity_type == "VPMOccurrence" or entity_type == "Container":
            self.set_path_vpm_occurrence(entity.as_pyclass(exp.VPMOccurrence))
        elif entity_type == "VPMReference":
            self.set_path_vpm_reference(entity)
        elif entity_type == "Body":
            self.path = f"**b_{entity.name()}{self.path}"
            self.set_path(entity.parent().parent())
        elif entity_type == "HybridBody":
            self.path = f"**g_{entity.name()}{self.path}"
            self.set_path(entity.parent())

    def set_path_vpm_occurrence(self, entity: exp.VPMOccurrence):
        self.set_path(entity.instance_occurrence_of().reference_instance_of())

    def set_path_vpm_reference(self, entity: exp.VPMReference):
        self.path = f"r_{entity.id()}_{entity.revision()}{self.path}"  

    def set_path_vpm_rep_reference(self, entity: exp.VPMRepReference):
        try:
            parent_ref = entity.father()
            self.set_path(parent_ref)
        except Exception:
            self.path = f"s_{entity.id()}_{entity.revision()}{self.path}"   