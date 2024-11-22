from collections.abc import Callable
from typing import List, TYPE_CHECKING

from application.observable_list import ObservableList

if TYPE_CHECKING:
    from application.application import Application
    from application.project import Project
    from application.variant import Variant

class Projects():
    def __init__(self, parent: 'Application'):
        self.application = parent
        self._parent = parent
        self._name = self.__class__.__name__
        self._project_collection = []
        self._project_collection: ObservableList['Project'] = ObservableList()
        # self._project_collection.add_observer(self._on_project_changed)

    def _on_project_changed(self, new_list: List['Project']):
        # Trigger UI update here
        print(self.__class__.__name__, "Projects collection updated:", new_list)
        # Call your UI binding logic, e.g., refreshing a ListBox in tkinter
        # self.application.parent.vm_look_editor.

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
    def project_collection(self) -> ObservableList['Project']:
        return self._project_collection

    @project_collection.setter
    def project_collection(self, value: ObservableList['Project']):
        self._project_collection = value

    @property
    def count(self) -> int:
        return len(self._project_collection)

    def get_project(self, project_id: str) -> 'Project':
        for project in self._project_collection:
            if project.id == project_id:
                return project
        return None
    
    def clean_empty_project(self) -> 'Projects':
        self.application.ready(lambda p: self._process_project_variants(p))
        return self
    
    def _process_project_variants(self, project: 'Project'):
        if project.variants.count == 0:
            project.active_variant = None
        else:
            self.application.status_message = f"activeProject: {project.name}.{project.active_variant.name}"
            # App.editors.variant_editor.dg_main.selected_item = project.active_variant
            self.application.parent.vm_variant_editor.selected_variant = project.active_variant

    def activate(self):
        def _set_active_project_variant(project: 'Project', variant: 'Variant'):
            # print(self.__class__.__name__, "activate", project.name)
            # self.application.active_project = project
            project.active_variant = variant

        def _activate_project():
            self.application.status_message = "Activating Project"
            ent = self.application.catia.services().product_service().root_occurrence().plm_entity()
            project = self.get_project(ent.id())
            # print(self.__class__.__name__, "id:", ent.id())

            if project is None:
                from application.project import Project
                project = Project(self, id=ent.id(), name=ent.title(), revision=ent.revision())
                self._project_collection.append(project)
                self.application.active_project = project
                project.load_configuration()
            else:
                # print(self.__class__.__name__, "Variant_not_ready", project.name)
                self.application.active_project = project
                project.variant_ready(lambda v: _set_active_project_variant(project, v))

            self.application.title = project.name  
            # self.application.projects.project_collection._notify_observers()

        self.application.catia_ready(lambda: _activate_project())

    # Public Sub Activate()
    #     App.CatiaReady(Sub()
    #                        App.StatusMessage = "Activating Project"
    #                        Dim ent As PLMModelerBaseIDL.PLMEntity = App.Catia.PLMProductService.RootOccurrence.PLMEntity
    #                        Dim p As CProject = GetProject(ent.ID)
    #                        If p Is Nothing Then
    #                            p = New CProject(Me) With {.Id = ent.ID, .Name = ent.V_Name, .Revision = ent.Revision}
    #                            _projectCollection.Add(p)
    #                            App.Model.ActiveProject = p
    #                            p.LoadConfiguration()
    #                            'p.ActiveVariant = Nothing
    #                        Else
    #                            p.VariantReady(Sub(v)
    #                                               App.Model.ActiveProject = p
    #                                               p.ActiveVariant = v
    #                                           End Sub)
    #                            App.Model.ActiveProject = p
    #                        End If

    #                        App.Title = p.Name
    #                    End Sub)
    # End Sub
