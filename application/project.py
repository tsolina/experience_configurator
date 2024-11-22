from __future__ import annotations
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List, Dict, Optional, TYPE_CHECKING
from application.tristate import Tristate
from application.variant import Variant
from application.variants import Variants
import experience as exp

from application.configurations import Configurations

if TYPE_CHECKING:
    from application.look_object import LookObject
    from application.configuration import Configuration
    
    from application.occurrence_object import OccurenceObject
    from application.projects import Projects

class Project:
    def __init__(self, parent: 'Projects', id:str="", name:str="", revision:str=""):
        self._parent = parent
        self.application = parent.application
        self.dict_looks: defaultdict[str, List['LookObject']] = defaultdict(list)
        self.targets_loaded = False
        self.look_actors: Dict[str, LookObject] = {}
        self._name = name or self.__class__.__name__
        self._id = id
        self._revision = revision
        self._configurations: Configurations = Configurations(self)
        self._active_configuration = None
        self._variants = Variants(self)
        self._active_variant = None
        self._occurrences = {}
        self.look_actors_lock = threading.Lock()

    @property
    def parent(self) -> 'Projects':
        return self._parent

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str):
        self._id = value

    @property
    def revision(self) -> str:
        if not self._revision:
            self._revision = "A"
        return self._revision

    @revision.setter
    def revision(self, value: str):
        self._revision = value

    @property
    def configurations(self) -> 'Configurations':
        return self._configurations

    @configurations.setter
    def configurations(self, value: 'Configurations'):
        self._configurations = value

    @property
    def active_configuration(self) -> 'Configuration':
        return self._active_configuration

    @active_configuration.setter
    def active_configuration(self, value: 'Configuration'):
        if self._active_configuration != value:
            self._active_configuration = value
            self.configurations.configuration_collection._notify_observers()

    @property
    def variants(self) -> 'Variants':
        return self._variants

    @variants.setter
    def variants(self, value: 'Variants'):
        self._variants = value 

    @property
    def active_variant(self) -> 'Variant':
        return self._active_variant

    @active_variant.setter
    def active_variant(self, value: 'Variant'):
        self._active_variant = value   

    def ready(self, cb: callable, cb_fail: callable):
        self.application.catia_ready(
            lambda: cb(self) if self._id == self.application.catia.services().product_service().root_occurrence().plm_entity().id() else cb_fail("Error: root is different"),
            lambda msg: cb_fail(msg)
        )

    def loop_occurrences(self, occurrences: exp.VPMOccurrences):
        for occ in occurrences:
            occurrence_obj = OccurenceObject(occ)
            if occurrence_obj.id() not in self._occurrences:
                self._occurrences[occurrence_obj.id()] = occurrence_obj
            self.loop_occurrences(occ.occurrences())

    @property
    def occurrences(self) -> Dict[str, 'OccurenceObject']:
        self.application.status_message = "Enumerating occurrences"
        self.application.catia_ready(lambda: self._initialize_root_occurrence())
        return self._occurrences

    @occurrences.setter
    def occurrences(self, value: Dict[str, 'OccurenceObject']):
        self._occurrences = value

    def _initialize_root_occurrence(self):
        root_occurrence = self.application.catia.services().product_service().root_occurrence()
        root_obj = OccurenceObject(root_occurrence)
        if root_obj.id not in self._occurrences:
            self._occurrences[root_obj.id] = root_obj
        self.loop_occurrences(root_occurrence.occurrences())

    def load_configuration0(self):
        tasks = [
            threading.Thread(target=self.application.xml.load_look.load),
            threading.Thread(target=self.application.xml.load_config.load)
        ]
        for task in tasks:
            task.start()
        for task in tasks:
            task.join()
    def load_configuration(self):
        self.application.xml.load_look.load()
        self.application.xml.load_config.load()

    def variant_ready(self, cb:Callable[['Variant'], None], cb_fail: Optional[callable] = None):
        if self.active_variant is None:
            if cb_fail:
                cb_fail("Error: no active variant is found")
            else:
                self.application.error_message = "no active variant is found"
        else:
            cb(self.active_variant)

    def config_ready(self, cb: Callable[['Configuration'], None], cb_fail: Optional[callable] = None):
        if self.active_configuration is None:
            message = "Error: no active look configuration is found"
            if cb_fail:
                cb_fail(message)
            else:
                self.application.status_message = message
        else:
            cb(self.active_configuration)

    def instantiate_missing_looks(self):
        self.application.look_file.ready(lambda look: [
            self._add_missing_look_configuration(tl) for tl in look.targets_list
        ])

    def _add_missing_look_configuration(self, target):
        found = any(c.active_look == target for c in self.configurations.configuration_collection)
        if not found:
            new_config = self.configurations.add()
            new_config.name = target
            new_config.active_look = target
            new_config.active_look_state = Tristate.OffState