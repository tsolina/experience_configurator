from typing import List, Optional, overload, TYPE_CHECKING
from application.observable_list import ObservableList
from application.tristate import Tristate

if TYPE_CHECKING:
    from application.configuration import Configuration
    from application.project import Project
    from application.look_container import LookContainer


class Configurations(ObservableList['Configuration']):
    def __init__(self, parent: 'Project'):
        super().__init__()  # Initialize ObservableList
        self._parent = parent
        self.application = parent.application
        self._name = self.__class__.__name__

        # You can now directly observe changes to the list through ObservableList's mechanisms
        self.add_observer(self._on_configuration_changed)

    def _on_configuration_changed(self, new_list: List['Configuration']):
        # Trigger UI update here
        # print(self.__class__.__name__, "Configuration collection updated:", "updating:", len(new_list), self.application.context.vm_look_editor)

        if not self.application.parent or not self.application.context.vm_look_editor:
            return 
        # print(self.__class__.__name__, "Configuration collection updated:", len(new_list))
        self.application.context.vm_look_editor.update_configurations()#new_list)

    @property
    def parent(self) -> 'Project':
        return self._parent

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    def add_empty_config(self) -> 'Configuration':
        config_id = len(self) + 1  # Use len(self) directly to get the size of the ObservableList
        from application.configuration import Configuration
        c = Configuration(parent=self, id=config_id, name=f"configuration.{config_id}", look_states=Tristate.to_toggle())

        def set_look_collection(look: 'LookContainer'):
            c.look_collection = list(look.targets_list)

        self.application.look_file.ready(lambda look: set_look_collection(look))

        self.application.sta_thread(lambda: self.append(c))  # Directly append using ObservableList's method
        return c
    
    @overload
    def add(self) -> 'Configuration':
        ...

    @overload
    def add(self, name:str="", active_state:str="", active_look:str="", container: Optional[ObservableList['Configuration']] = None) -> 'Configuration':
        ...

    def add(self, name:str="", active_state:str="", active_look:str="", container: Optional[ObservableList['Configuration']] = None) -> 'Configuration':
        if container is None:
            return self.add_empty_config()

        from application.configuration import Configuration
        id = len(container) + 1
        configuration = Configuration(parent=self, id=id, name=name or f"configuration.{id}", look_states=Tristate.to_toggle(), active_state=active_state, active_look=active_look)
        container.append(configuration)
        
        return configuration
    
    def delete(self) -> 'Configurations':
        active_config = self.parent.active_configuration
        if active_config is None:
            self.application.error_message = "Delete unsuccessful, no configuration selected"
            return self

        active_id = active_config.id
        active_config.actors.clear()

        index = self.index(active_config)

        self.parent.active_configuration = None
        self.remove(self[index])

        for config in self:
            if config.id > active_id:
                config.id -= 1

        self.application.status_message = "Ready"
        return self
    
    def for_each(self, callback):
        for config in self:
            callback(config)

    # def __del__(self):
    #     # Clean-up code equivalent to Finalize
    #     self.clear()  # Use clear method from ObservableList to empty the list
