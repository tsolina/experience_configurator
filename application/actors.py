from typing import List, Callable, Optional
from collections import namedtuple

from application.actor import Actor
from application.configuration import Configuration
from application.eval_selected import EvalSelected
from application.observable_list import ObservableList
import experience as exp

class Actors:
    def __init__(self, parent: Configuration):
        self._parent = parent
        self.application = parent.application
        self._name = "Actors"
        self.actor_list: ObservableList[Actor] = ObservableList()

    @property
    def parent(self) -> Configuration:
        return self._parent

    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def count(self) -> int:
        return len(self.actor_list)
    
    def select_actor(self, i_actor) -> Actor:
        ok = EvalSelected(self.application, i_actor)
        actor = Actor(self, id=len(self.actor_list) + 1, name=ok.name, type_=ok.type_, cat_object=ok.cat_obj, path=ok.path, err_message=ok.message)

        self.actor_list.append(actor)
        self.parent.active_actor = actor
        return actor
    
    def select_actors(self) -> 'Actors':
        sel = self.application.catia.active_editor().selection()

        def process_item(item: exp.SelectedElement):
            ok = EvalSelected(self.application, item.value())
            
            if ok.message == "":
                for a in self.actor_list:
                    if ok.message != "":
                        break
                    
                    if a.path == ok.path:
                        ok.message = f"object already in list, {ok.name}"
                        break

                if ok.message != "":
                    self.application.error_message = ok.message
                    return  # Exit function if there's an error

                actor = Actor(self, id=len(self.actor_list) + 1, name=ok.name, type_=ok.type_, cat_object=ok.cat_obj, path=ok.path, err_message=ok.message)
                self.actor_list.append(actor)

                self.application.look_validator.validate(actor)
            else:
                self.application.error_message = ok.message

        # Perform actions using selection
        if sel.count():
            sel.for_each(process_item)            

        # Set the last actor in the list as the active actor
        if self.actor_list:
            self.parent.active_actor = self.actor_list[-1]

        return self
    
    def reselect_actor(self) -> 'Actors':
        # Simulated selection logic
        selection = self.parent.active_actor
        if not selection:
            return self

        ok = EvalSelected(self.application, selection.cat_object)
        if ok.message is None:
            for existing_actor in self.actor_list:
                if existing_actor.path == ok.path:
                    ok.message = f"Object already in list, {ok.name}"
                    return self

            actor = self.parent.active_actor
            actor.name = ok.name
            actor.type_ = ok.type_
            actor.cat_object = ok.cat_obj
            actor.path = ok.path
            actor.err_message = None
            self.check_actor_error()

        return self
    
    def check_actor_error(self):
        self.application.error_message = "E" if any(actor.err_message for actor in self.actor_list) else ""
    
    def deselect_actors(self) -> "Actors":
        def use_selection(sel:exp.Selection):
            if sel.count() == 0:
                return self
            
            def process_item(item:exp.SelectedElement):
                ok:EvalSelected = EvalSelected(self.application, item.value())

                if ok.message:
                    self.application.status_message = ok.message
                    return
                
                for actor in self.actor_list:
                    if ok.message:
                        break

                    if actor.path == ok.path:
                        self.application.look_validator.invalidate(actor)
                        self.parent.active_actor = actor
                        self.delete_actor()

            sel.for_each(process_item)

        self.application.selection(use_selection)
        return self

    
    def delete_actor(self) -> 'Actors':
        active_actor = self.parent.active_actor
        if active_actor is None:
            print("Delete failed, no actor selected")
            return self

        self.actor_list = [actor for actor in self.actor_list if actor.id != active_actor.id]
        for actor in self.actor_list:
            if actor.id > active_actor.id:
                actor.id -= 1

        self.parent.active_actor = None
        self.check_actor_error()
        return self
    
    def delete_actor(self) -> 'Actors':
        if self.parent.active_actor is None:
            self.application.status_message = "Delete failed, no actor selected"
            return self
        
        active_id = self.parent.active_actor.id
        self.application.status_message = "Actor deleted"

        self.actor_list.remove(self.parent.active_actor)
        self.parent.active_actor = None

        for actor in self.actor_list:
            if actor.id > active_id:
                actor.id -= 1
        
        self.application.look_validator.validate(self.parent, False)

        self.check_actor_error()

        return self
    
    def for_each(self, callback: Callable[[Actor], None]):
        for actor in self.actor_list:
            callback(actor)

    def __del__(self):
        self.actor_list = []