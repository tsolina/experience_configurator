from typing import TYPE_CHECKING, List, Optional
from application.observable_list import ObservableList

if TYPE_CHECKING:
    from application.application import Application
    from application.project import Project
    from application.variant import Variant


class Projects(ObservableList['Project']):
    def __init__(self, parent: 'Application'):
        super().__init__()
        self.application = parent
        self._parent = parent
        self._name = self.__class__.__name__
        self.add_observer(self._on_project_changed)

    def _on_project_changed(self, new_list: List['Project']):
        # Trigger UI update here
        print(self.__class__.__name__, "Projects collection updated:", new_list)

    @property
    def parent(self) -> 'Application':
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

    def get_project(self, project_id: str) -> Optional['Project']:
        for project in self:
            if project.id == project_id:
                return project
        return None

    def clean_empty_project(self) -> 'Projects':
        self.application.ready(lambda p: self._process_project_variants(p))
        return self

    def _process_project_variants(self, project: 'Project'):
        if len(project.variants) == 0:
            project.active_variant = None
        else:
            self.application.status_message = f"activeProject: {project.name}.{project.active_variant.name}"
            self.application.parent.vm_variant_editor.selected_variant = project.active_variant

    def activate(self):
        def _set_active_project_variant(project: 'Project', variant: 'Variant'):
            project.active_variant = variant

        def _activate_project():
            self.application.status_message = "Activating Project"
            ent = self.application.catia.services().product_service().root_occurrence().plm_entity()
            project = self.get_project(ent.id())

            if project is None:
                from application.project import Project
                project = Project(self, id=ent.id(), name=ent.title(), revision=ent.revision())
                self.append(project)
                self.application.active_project = project
                project.load_configuration()
            else:
                self.application.active_project = project
                project.variant_ready(lambda v: _set_active_project_variant(project, v))

            self.application.title = project.name

        self.application.catia_ready(lambda: _activate_project())
