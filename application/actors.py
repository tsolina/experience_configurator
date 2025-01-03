from typing import TYPE_CHECKING, Callable, List, Optional, Union, overload
from application.observable_list import ObservableList
from application.eval_selected import EvalSelected
import experience as exp

if TYPE_CHECKING:
    from application.actor import Actor
    from application.configuration import Configuration


class Actors(ObservableList['Actor']):
    def __init__(self, parent: 'Configuration'):
        super().__init__()
        self._parent = parent
        self.application = parent.application
        self._name = self.__class__.__name__
        self.status_update_error:Callable[[str], None] = self.application.context.services.status.status_update_error
        self.status_update:Callable[[str], None] = self.application.context.services.status.status_update

        self.add_observer(self._on_actors_changed)

    def _on_actors_changed(self, new_list: List['Actor']):
        # Trigger UI update here
        # print(self.__class__.__name__, "Actors collection updated:", "updating:", len(new_list), self.application.context.vm_look_editor)

        if not self.application.parent or not self.application.context.vm_look_editor:
            return 
        # print(self.__class__.__name__, "Actors collection updated:", len(new_list))
        self.application.context.vm_look_editor.update_actors(new_list)

    @property
    def parent(self) -> 'Configuration':
        return self._parent

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def count(self) -> int:
        return len(self)

    def select_actor(self, i_actor:exp.AnyObject) -> 'Actor':
        ok = EvalSelected(self.application, i_actor)
        # print(__name__, "select_actor.ok", ok, ok.message, ok.name, ok.path, ok.type_)
        actor = self._create_actor(ok)
        self.append(actor)
        self.parent.active_actor = actor
        return actor


    @overload
    def select_actors(self, i_actor: exp.AnyObject) -> 'Actors':  # Single actor overload
        ...

    @overload
    def select_actors(self) -> 'Actors':  # Multiple actors overload
        ...

    def select_actors(self, i_actor:exp.AnyObject=None):   
        # print(__name__, "select_actors.is_ok", i_actor is not None)     
        if i_actor is not None:
            self.select_actor(i_actor)
            return self

        def select_items(sel:exp.Selection):
            for item in sel:
                ok = EvalSelected(self.application, item.value())
                if not ok.message:
                    for a in self:
                        if ok.message:
                            break
                        if a.path == ok.path:
                            ok.message = f"Object already in list, {ok.name}"
                            break

                    if ok.message:
                        self.status_update_error(ok.message)
                        continue
                    
                    from application.actor import Actor
                    actor = Actor(self, id = len(self)+1, name=ok.name, type_=ok.type_, cat_object=ok.cat_obj, path=ok.path)

                    self.append(actor)
                    self.application.look_validator.validate(actor)
                else:
                    self.status_update_error(ok.message)

            if len(self) > 0:
                self.parent.active_actor = self[-1]

        self.application.context.services.selection.active_selection(select_items, self.status_update)

        return self

    def _is_actor_valid(self, ok: EvalSelected) -> bool:
        if ok.message:
            self.status_update_error(ok.message)
            return False

        for actor in self:
            if actor.path == ok.path:
                self.status_update_error(f"Object already in list, {ok.name}")
                return False

        return True

    def _create_actor(self, ok: EvalSelected) -> 'Actor':
        from application.actor import Actor
        return Actor(
            self,
            id=len(self) + 1,
            name=ok.name,
            type_=ok.type_,
            cat_object=ok.cat_obj,
            path=ok.path,
            err_message=ok.message
        )

    def reselect_actor(self) -> 'Actors':
        selection = self.parent.active_actor
        if not selection:
            return self

        ok = EvalSelected(self.application, selection.cat_object)
        if ok.message:
            self.status_update_error(ok.message)
            return self

        for actor in self:
            if actor.path == ok.path:
                self.status_update_error(f"Object already in list, {ok.name}")
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
        self.status_update_error("E" if any(actor.err_message for actor in self) else "")

    def deselect_actors(self) -> 'Actors':
        def process_selection(sel: exp.Selection):
            def process_item(item: exp.SelectedElement):
                ok = EvalSelected(self.application, item.value())
                if ok.message:
                    self.status_update(ok.message)
                    return

                actor_to_remove = next((actor for actor in self if actor.path == ok.path), None)
                if actor_to_remove:
                    self.application.look_validator.invalidate(actor_to_remove)
                    self.remove(actor_to_remove)

            sel.for_each(process_item)

        self.application.context.services.selection.active_selection(process_selection)
        return self

    def delete_actor(self) -> 'Actors':
        active_actor = self.parent.active_actor
        if not active_actor:
            self.status_update("Delete failed, no actor selected")
            return self

        active_id = active_actor.id
        self.remove(active_actor)
        self.parent.active_actor = None

        for actor in self:
            if actor.id > active_id:
                actor.id -= 1

        self.application.look_validator.validate(self.parent, False)
        self.check_actor_error()
        return self

    def for_each(self, callback: Callable[['Actor'], None]):
        for actor in self:
            callback(actor)

