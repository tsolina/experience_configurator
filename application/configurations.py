from typing import List, Optional, overload, TYPE_CHECKING
from application.observable_list import ObservableList
from application.tristate import Tristate

if TYPE_CHECKING:
    from application.configuration import Configuration
    from application.project import Project
    from application.look_container import LookContainer


class Configurations:
    def __init__(self, parent: 'Project'):
        self._parent = parent
        self.application = parent.application
        self._name = self.__class__.__name__
        # self._configuration_collection = ['Configuration']
        self._configuration_collection: ObservableList['Configuration'] = ObservableList()
        # self._configuration_collection.add_observer(self._on_configuration_changed)

    def _on_configuration_changed(self, new_list: List['Configuration']):
        # Trigger UI update here
        print(self.__class__.__name__, "Configuration collection updated:", len(new_list))
        # Call your UI binding logic, e.g., refreshing a ListBox in tkinter
        # self.application.projects.project_collection._notify_observers()

    @property
    def parent(self) -> 'Project':
        return self._parent

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def configuration_collection(self) -> ObservableList['Configuration']:
        return self._configuration_collection

    @configuration_collection.setter
    def configuration_collection(self, value:ObservableList['Configuration']):
        self._configuration_collection = value

    def add_empty_config(self) -> 'Configuration':
        config_id = len(self._configuration_collection) + 1
        from application.configuration import Configuration
        c = Configuration(parent=self, id=config_id, name=f"configuration.{config_id}", look_states=Tristate.to_toggle())

        def set_look_collection(look:'LookContainer'):
            c.look_collection = list(look.targets_list)

        self.application.look_file.ready(lambda look: set_look_collection(look))

        self.application.sta_thread(lambda: self._configuration_collection.append(c))
        return c
    
    @overload
    def add(self) -> 'Configuration':
        ...
    
    @overload
    def add(self, container:List['Configuration']):
        ...
    
    def add(self, container:Optional[List['Configuration']] = None) -> 'Configuration':
        if not container:
            return self.add_empty_config()
        
        from application.configuration import Configuration
        id = len(container)+1
        configuration = Configuration(parent=self, id=id, name=f"configuration.{id}", look_states=Tristate.to_toggle())
        self.application.look_file.ready(lambda look: setattr(configuration, "look_collection", look.targets_list))

        # container.append(configuration)
        self.application.sta_thread(lambda: container.append(configuration))
        return configuration
    
    
    def delete(self) -> 'Configurations':
        if self.parent.active_configuration is None:
            self.application.error_message = "Delete unsuccessful, no configuration selected"
            return self
        print(self.__class__.__name__, "config", self.parent.active_configuration.id, self.parent.active_configuration.name)
        active_id = self.parent.active_configuration.id
        self.parent.active_configuration.actors.actor_list.clear()
        self._configuration_collection.remove(self.parent.active_configuration)

        for config in self._configuration_collection:
            if config.id > active_id:
                config.id -= 1

        self.application.status_message = "Ready"
        return self
    
    def for_each(self, callback):
        for config in self._configuration_collection:
            callback(config)

    def __del__(self):
        # Clean-up code equivalent to Finalize
        self._configuration_collection = None