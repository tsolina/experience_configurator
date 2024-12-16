from typing import List, Dict, Callable, TYPE_CHECKING
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
import time

from application.look_container import LookContainer
import experience as exp

if TYPE_CHECKING:
    from application.application import Application


class LookFile():
    def __init__(self, parent: 'Application'):
        self._look = LookContainer()
        self.targets_list: List[str] = []
        self.targets_dict: Dict[str, 'exp.Material'] = {}
        self.variants_list: List[str] = []
        self.variants_dict: Dict[str, 'exp.Material'] = {}
        self._parent = parent
        self.application = parent
        self._name = self.__class__.__name__
        self._lock = Lock()

    @property
    def parent(self):
        return self._parent

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    def set_look_part(self):
        for editor in self.application.catia.editors():
            try:
                if editor.active_object().name() == "VIZ_LOOK_LIBRARY A.1":
                    self._look.part = editor.active_object()
                elif editor.active_object().name() == "VIZ_LOOK_LIBRARY":
                    ro = editor.active_object(exp.VPMRootOccurrence)
                    ri = ro.reference_root_occurrence_of().rep_instances().item(1)
                    self._look.part = ri.reference_instance_of().part()
            except Exception:
                continue

    def load_look_part(self):
        if self._look.part is not None:
            return

        window = self.application.catia.active_window()
        search_service = self._parent.catia.services().search_service()
        db_search = search_service.database_search().base_type("VPMReference").add_easy_criteria("V_Name", "VIZ_LOOK_LIBRARY")
        search_service.search()

        if db_search.results().count() == 0:
            self._look.err_msg = "reference VIZ_MATERIALS part not found"
            return

        look_editor = None
        self.application.catia.services().open_service().plm_open(db_search.results().item(1), look_editor)
        self.application.catia.active_window().active_viewer().create_viewer_3d().rendering_mode("catRenderMaterial") 

        self.application.util.do_events()
        time.sleep(2)
        self.application.util.do_events()
        window.activate()

        self.set_look_part() 

    def set_look_container(self):
        with ThreadPoolExecutor() as executor:
            executor.submit(lambda: self._look.targets_list.extend(["No Look"] + self.targets_list))
            executor.submit(lambda: {self._look.targets_dict.update({key: self.targets_dict[key]}) for key in self.targets_dict})
            executor.submit(lambda: self._look.variants_list.extend(self.variants_list + self.targets_list))
            executor.submit(lambda: {self._look.variants_dict.update({key: self.variants_dict[key]}) for key in self.variants_dict})
    
    def extract_covering_materials(self):
        mats_in_session = self.application.catia.services().mat_plm_service().get_materials_in_session()

        for i in range(1, mats_in_session.count() + 1):
            material:exp.Material = mats_in_session.item(i)
            if material.get_custom_type() == "dsc_matref_ref_Covering":
                if material.name().lower().startswith("t_") and material.name() not in self.targets_list:
                    self.targets_list.append(material.name())
                    self.targets_dict[material.name()] = material
                elif material.name().lower().startswith("v_") and material.name() not in self.variants_list:
                    self.variants_list.append(material.name())
                    self.variants_dict[material.name()] = material

        self.targets_list.sort()
        self.variants_list.sort()

        self.set_look_container()

    def ready(self, cb: Callable[['LookContainer'], None], cb_fail: Callable[[str], None] = None):
        if self._look.part is None:
            with self._lock:
                if self._look.part is None:
                    def on_ready():
                        self.application.status_message = "Loading file with looks"
                        self.set_look_part()
                        self.load_look_part()
                        if self._look.part is None:
                            if cb_fail:
                                cb_fail(self._look.err_msg)
                        else:
                            self.extract_covering_materials()
                            cb(self._look)

                    self.application.context.services.catia.ready(on_ready, cb_fail)
                else:
                    cb(self._look)
        else:
            cb(self._look)

    def __del__(self):
        self._look = None
        self.targets_list.clear()
        self.targets_dict.clear()
        self.variants_list.clear()
        self.variants_dict.clear()