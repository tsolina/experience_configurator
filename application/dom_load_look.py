import os
import threading
from tkinter import filedialog, messagebox
from xml.etree import ElementTree as ET
from threading import Lock
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, TYPE_CHECKING

from application.actor_catia import ActorCatia
from application.configuration import Configuration
from application.look_container import LookContainer
from application.look_object import LookObject
from application.occurrence_object import OccurenceObject
from application.project import Project
from application.task_model import TaskModel
from xml.dom.minidom import parse, parseString
from lxml import etree
import experience as exp

if TYPE_CHECKING:
    from application.xml import XML

class DomLoadLook:
    def __init__(self, parent:'XML'):
        self.application = parent.application
        self._save_path = "C:/Users/tomislav.solina/Desktop/3dx/viz"
        self._file_path = None
        self.XDoc:etree._ElementTree = None
        self.xtop_node = None
        self.lock = Lock()

    @property
    def _file_name(self):
        project = self.application.active_project
        return f"{project.id}_{project.revision}.xml"
    
    def add_actor_if_is_new(self, _co:'LookObject', _look:list['LookObject']):
        """
        Adds the given LookObject to the list if it is not already present.
        
        Args:
            _co (LookObject): The look object to add.
            _look (List[LookObject]): The list of look objects.
        """
        with threading.Lock():  # Equivalent of SyncLock in VB.NET
            # Check if _co is already in the list
            _to = next((a for a in _look if a == _co), None)
            if _to is None:
                _look.append(_co)



    def select_body(self, actor: str, _co: 'LookObject', cfg: 'Configuration', _look: list['LookObject'], path: str, _part: exp.Part):
        """
        Handle the selection of a body for the given actor.

        Args:
            actor (str): The name of the actor.
            _co (LookObject): The look object to update.
            cfg (Configuration): The configuration object.
            _look (ist[CLookObject]): The list of look objects.
            iPath (str): The hierarchical path of the body to find.
            _part (Part): The part object that contains bodies.
        """
        path = path[2:]

        if _part.bodies().contains(path):
            b = _part.bodies().item(path)

            _co.actor.cat_object = b
            _co.actor.type_ = "Body"
            _co.target_name = cfg.active_look

            self.add_actor_if_is_new(_co, _look)

            cfg.actors.select_actors(b)

            with threading.Lock():
                if _co.actor.path not in self.application.active_project.look_actors:
                    self.application.active_project.look_actors[_co.actor.path] = _co
        else:
            self.select_not_found(actor, "Body", cfg)



    def select_set(self, actor: str, co: 'LookObject', cfg: 'Configuration', look: List['LookObject'], path: str, sets: exp.HybridBodies) -> None:
        """
        Handle the selection of a set (HybridBody) for a given actor.

        Args:
            actor (str): The name of the actor.
            co (LookObject): The look object to update.
            cfg (Configuration): The configuration object.
            look (List[LookObject]): The list of look objects.
            path (str): The hierarchical path of the set to find.
            sets (HybridBodies): The collection of hybrid bodies to search within.
        """
        # Remove the first two characters of the path
        path = path[2:]

        if "**" in path:
            sub_path_index = path.find("**") + 2
            sub_path = path[sub_path_index:]
            path = path.replace(sub_path, "").replace("*", "")

            if sets.contains(path):
                gs = sets.item(path)
                sub_sets = gs.hybrid_bodies()
                self.select_set(actor, co, cfg, look, sub_path, sub_sets)
        else:
            if sets.contains(path):
                gs = sets.item(path)

                co.actor.cat_object = gs
                co.actor.type_ = gs.com_type()
                co.target_name = cfg.active_look

                self.add_actor_if_is_new(co, look)

                cfg.actors.select_actors(gs)

                # Thread-safe addition to the global look actors
                with self.application.active_project.look_actors_lock:
                    if co.actor.path not in self.application.active_project.look_actors:
                        self.application.active_project.look_actors[co.actor.path] = co
            else:
                self.select_not_found(actor, "HybridBody", cfg)



    def select_not_found(self, actor: str, actor_type: str, cfg: 'Configuration') -> None:
        """
        Handle the case where an actor is not found in the configuration.

        Args:
            actor (str): The name or identifier of the actor.
            actor_type (str): The type of the actor (e.g., "Container").
            cfg (CConfiguration): The configuration object to update.
        """
        # Select an actor with a default value (None in this case)
        selected_actor = cfg.actors.select_actor(None)

        # Set the attributes of the selected actor
        selected_actor.name = actor
        selected_actor.type_ = actor_type
        selected_actor.path = actor


    def select_reference(self, actor: str, _co: 'LookObject', cfg: 'Configuration', _look: List['LookObject'], occ: Dict[str, 'OccurenceObject']) -> None:
        """Selects a reference based on the actor string and updates the configuration."""
        # Trim the first two characters from the actor string
        actor = actor[2:]

        if "**" in actor:
            # Extract the sPath after '**'
            s_path = actor.split("**", 1)[1]
            actor = actor.replace(s_path, "").replace("*", "")

            # Remove the portion after the last underscore
            if "_" in actor:
                actor = actor.rsplit("_", 1)[0]

            if actor in occ:
                vpm_ref = occ[actor].reference
                _part = vpm_ref.rep_instances().item(1).reference_instance_of().part()

                if s_path.startswith("b_"):
                    self.select_body(actor, _co, cfg, _look, s_path, _part)
                elif s_path.startswith("g_"):
                    _sets = _part.hybrid_bodies
                    self.select_set(actor, _co, cfg, _look, s_path, _sets)
            else:
                self.select_not_found(actor, "Container", cfg)
        else:
            # Remove the portion after the last underscore
            if "_" in actor:
                actor = actor.rsplit("_", 1)[0]

            if actor in occ:
                _co.actor.cat_object = occ[actor].occurence
                _co.actor.type_ = "Container"
                _co.target_name = cfg.active_look

                self.add_actor_if_is_new(_co, _look)

                cfg.actors.select_actors(_co.actor.cat_object)

                # Thread-safe update of LookActors
                with self.application.active_project.look_actors_lock:
                    if _co.actor.path not in self.application.active_project.look_actors:
                        self.application.active_project.look_actors[_co.actor.path] = _co
            else:
                self.select_not_found(actor, "Container", cfg)


    def prompt_user(self, message: str, title: str) -> bool:
        return messagebox.askokcancel(title, message)

    def inspect_xml_header(self, header: Optional[etree._Element], is_import: bool) -> bool:
        """Inspect the XML header for validity and optional import check."""
        if header is None:
            self.application.error_message = "no header found"
            return False

        # Extract the generator node text if it exists
        generator = header.xpath("./generator/text()")
        generator = generator[0] if generator else ""

        if not generator:
            self.application.error_message = "document invalid, not look configurator document"
            return False

        if generator != "Look configurator by TSolina":
            self.application.error_message = "document invalid, not look configurator document"
            return False

        if is_import:
            # Extract the ID node text if it exists
            doc_id = header.xpath("./id/text()")
            doc_id = doc_id[0] if doc_id else ""

            if doc_id != self.application.active_project.id:
                # Prompt the user for confirmation
                result = self.prompt_user(
                    "xml of another file detected, sure to import?", 
                    "3DExperience configurator | import look"
                )
                if not result:
                    self.application.error_message = "look import cancelled"
                    return False

        return True

    def evaluate_xml(self, is_import: bool):
        self.XDoc = None
        self.application.status_message = "loading looks"
        project = self.application.active_project

        try:
            # Parse the XML file using lxml
            self.XDoc = etree.parse(self._file_path)
        except Exception as ex:
            self.application.error_message = "Corrupted .xml document"
            return

        # Select the header node using XPath
        header = self.XDoc.xpath("//model/header")
        if not self.inspect_xml_header(header, is_import):
            return

        # Select all configuration nodes using XPath
        configs:List[etree.Element] = self.XDoc.xpath("//model/lookConfigurator/configuration")
        if len(configs) == 0:
            self.application.error_message = "no configurations found"
            return

        cnt = []  # Equivalent to ObservableCollection in Python, can be a list
        nCount = 1
        occ = project.occurrences

        for config in configs:
            # Extract the values using XPath and .text to get inner text
            sName = config.xpath("./name/text()")[0]
            sLook = config.xpath("./look/text()")[0]
            sState = config.xpath("./state/text()")[0]

            _look = []
            # Simulating Add() function for configurations (you can replace with actual logic)
            c:Configuration = project.configurations.add(cnt)
            c.name = sName
            c.active_look_state = sState
            c.active_look = sLook

            if sState == "On":
                if sLook in project.dict_looks:
                    _look = project.dict_looks[sLook]
                else:
                    _look = []
                    project.dict_looks[sLook] = _look

                tasks = []
                actors = config.xpath("./actors/actor")
                for actor in actors:
                    actor_name = actor.text
                    _co = LookObject()
                    _co.actor = ActorCatia(path=actor.text)

                    def task(actor_name=actor_name, _co=_co):
                        self.select_reference(actor_name, _co, c, _look, occ)

                    tasks.append(TaskModel(task))

                self.application.parent.wait_tasks(tasks)


            self.application.status_message = f"looks: {nCount} of {len(configs)} loaded: {c.name}"
            nCount += 1

        # Updating the configurations collection
        project.configurations.configuration_collection = cnt

        def update_ui():
            self.application.parent.vm_look_editor.selected_configuration = project.configurations.configuration_collection[0]
            project.active_configuration = project.configurations.configuration_collection[0]
        self.application.sta_thread(lambda: update_ui())

        if is_import:
            self.application.status_message = f"look configuration imported: {self._file_path}"
        else:
            self.application.status_message = f"configuration loaded: {self._file_name}"


    def select_reference(self, actor: str, _co: 'LookObject', cfg: 'Configuration', _look: List['LookObject'], occ: Dict[str, 'OccurenceObject']) -> None:
        # Remove the first two characters from the actor string
        actor = actor[2:]

        if "**" in actor:
            s_path = actor[actor.find("**") + 2:]
            actor = actor.replace(s_path, "").replace("*", "")
            if "_" in actor:
                actor = actor[:actor.rfind("_")]

            if actor in occ:
                vpm_ref = occ[actor].reference
                _part = vpm_ref.rep_instances().item(1).reference_instance_of().part()

                if s_path.startswith("b_"):
                    self.select_body(actor, _co, cfg, _look, s_path, _part)
                elif s_path.startswith("g_"):
                    _sets = _part.hybrid_bodies
                    self.select_set(actor, _co, cfg, _look, s_path, _sets)
            else:
                self.select_not_found(actor, "Container", cfg)
        else:
            if "_" in actor:
                actor = actor[:actor.rfind("_")]

            if actor in occ:
                _co.actor.cat_object = occ[actor].occurence # catia item- cat_object:VPMOccurrence, VPMRootOccurrence
                _co.actor.type_ = "Container"
                _co.target_name = cfg.active_look

                self.add_actor_if_is_new(_co, _look)

                cfg.actors.select_actors(_co.actor.cat_object)
                with threading.Lock():
                    if _co.actor.path not in self.application.active_project.look_actors:
                        self.application.active_project.look_actors[_co.actor.path] = _co
            else:
                self.select_not_found(actor, "Container", cfg)




    def load(self):
        self._file_path = os.path.join(self.application.registry.base_path, self._file_name)
        if not os.path.exists(self._file_path):
            self.application.error_message = f"{self._file_path} not found"
            return self
        self.clean_look_configuration()
        self.application.look_file.ready(lambda: self.evaluate_xml(False))
        return self

    def clean_look_configuration(self):
        def clear_configuration(p:'Project'):
            if p.active_configuration is not None:
                p.active_configuration.actors.actor_list.clear()
                p.configurations.configuration_collection.clear()

        self.application.project_ready(clear_configuration)
        return self

    def open_dialog(self):
        file_path = ""

        options = {
            "filetypes": [("XML Files", "*.xml")],
            "initialdir": self.application.registry.base_path,
            "title": "Import look configuration from .xml",
        }
        file_path = filedialog.askopenfilename(**options)

        return file_path

    def import_file(self):
        self._file_path = self.open_dialog()
        if not self._file_path:
            return self
        if self.application.active_project.configurations.configuration_collection:
            result = input("Do you want to add to existing configuration? (yes/no): ")
            if result.lower() != "yes":
                self.clean_look_configuration()
        self.evaluate_xml(True)
        return self



    def activate(self):
        def process_look(look:'LookContainer'):
            def process_model(p:'Project'):
                for d_key in p.dict_looks.keys():
                    def process_key():
                        if d_key in look.targets_dict:
                            d_list = p.dict_looks[d_key]

                            def process_look_object(a:'LookObject'):
                                def add_look_task():
                                    a.desired_look = d_key
                                    self.application.look.add_look(a)
                                self.application.run_task(add_look_task)

                            for a in d_list:
                                process_look_object(a)
                    self.application.run_task(process_key)
                p.targets_loaded = True

            self.application.project_ready(process_model)

        self.application.look_file.ready(process_look)

