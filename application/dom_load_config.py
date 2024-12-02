from tkinter import filedialog, messagebox
from typing import List, Optional, Callable, TYPE_CHECKING
from lxml import etree
import os

if TYPE_CHECKING:
    from application.xml import XML
    from application.application import Application
    from application.look_container import LookContainer
    from application.project import Project
    from application.switch import Switch    
from application.variant import Variant
from application.tristate import Tristate
import experience as exp

class DomLoadConfig:
    def __init__(self, parent: 'XML') -> None:
        self.application = parent.application
        self._filePath: str = ""
        self.XDoc: Optional[etree._ElementTree] = None
        self.XTopNode: Optional[etree._Element] = None
        self._actor: str = ""
        self._sel: exp.Selection = self.application.catia.active_editor().selection()
        self._part: Optional[exp.Part] = None
        self._sets: Optional[exp.HybridBodies] = None
        self._dictRefs: dict[str, exp.VPMReference] = {}

    @property
    def _file_name(self) -> str:
        return f"cfg_{self.application.active_project.id}.xml"

# self.create_switch(v, sType[0] if sType else "", sActor[0] if sActor else "", sValue[0] if sValue else "", stateValue[0])
    def create_switch(self, iVariant: 'Variant', iType:str="", iActor:str="", iValue:str="", iState:str="") -> None:
        s: Optional['Switch'] = None
        iVariant.active_sub_variant = iVariant.sub_variants.get_sub_variant(iState)
        if iType == "Look":
            s = iVariant.active_sub_variant.switches.add_look()
            s.name_var.set(iActor)
        elif iType == "CodeState":
            s = iVariant.active_sub_variant.switches.add_code_style()
            s.name_var.set(iActor)
            s.actor_collection = [s.name]
        elif iType == "Visibility":
            s = iVariant.active_sub_variant.switches.add_visible()
            s.name_var.set(iActor)
            s.actor_collection = [s.name]
        else:
            print(iType)
            s = iVariant.active_sub_variant.switches.add_visible()
            s.actor_collection = [s.name]

        s.active_value_var.set(iValue)

    def evaluate_xml(self, is_import: bool) -> None:
        self.XDoc = etree.ElementTree()
        try:
            self.XDoc.parse(self._filePath)
        except etree.XMLSyntaxError:
            self.application.error_message = "corrupted .xml document"
            return

        header = self.XDoc.xpath("//model/header")
        if not header:
            self.application.error_message = "no header found"
            return

        header = header[0]
        sGenerator = header.xpath("./generator/text()")
        if not sGenerator:
            self.application.error_message = "document invalid, not variant configurator document"
            return
        if sGenerator[0] != "Configurator by TSolina":
            self.application.error_message = "document invalid, not variant configurator document"
            return

        if is_import:
            sId = header.xpath("./id/text()")

            if sId != self.application.active_project.id:
                result = messagebox.askokcancel(
                    title="3DExperience Configurator | Import Variant",
                    message="XML of another file detected. Are you sure you want to import?"
                )
                if not result:  # User clicked 'Cancel'
                    self.application.error_message = "Look import cancelled."
                    return
                else:  # User clicked 'OK'
                    self.application.status_message = "Importing variant configuration."

        configs:List[etree.Element] = self.XDoc.xpath("//model/configurator/variant")
        if len(configs) == 0:
            self.application.status_message = "no configurations found"
            return

        self.application.flags.no_status_messages = True
        # cnt = []
        nCount = 1
        for config in configs:
            sName = config.xpath("./name/text()")[0]
            sActive = config.xpath("./activeState/text()")[0].strip() or ""

            v:Variant = None
            # v = self.application.active_project.variants.add(cnt)
            v = self.application.active_project.variants.add(name=sName, active_state=sActive, container=self.application.active_project.variants)

            states = config.xpath("./state")
            for state in states:
                stateValue = state.xpath("./value/text()")[0]
                if not stateValue:
                    continue
                v.active_state_var.set(stateValue)

                switches = state.xpath("./switches/switch")
                for switch in switches:
                    sType = switch.xpath("./type/text()")[0]
                    sActor = switch.xpath("./actor/text()")[0]
                    sValue = switch.xpath("./value/text()")[0]

                    # self.create_switch(v, sType[0] if sType else "", sActor[0] if sActor else "", sValue[0] if sValue else "", stateValue[0])
                    self.create_switch(v, sType, sActor, sValue, stateValue)

            v.active_state = v.editing_state = sActive

            self.application.status_message = f"variants: {nCount} of {len(configs)} loaded: {sName[0]}"
            nCount += 1

        self.application.flags.no_status_messages = False

        # self.application.active_project.variants = cnt

        # def assign_item():
        #     self.application.context.vm_variant_editor.selected_variant = self.application.active_project.variants[0]

        # self.application.sta_thread(assign_item)

        if is_import:
            self.application.status_message = f"look configuration imported: {self._filePath}"
        else:
            self.application.status_message = f"configuration loaded: {self._file_name}"


    def activate(self) -> None:
        self.application.catia.refresh_display(False).hso_synchronized(False)

        def activate_project(project:'Project'):
            project.variants.for_each(lambda v: self.application.validator.validate(v) if v.active_state == Tristate.OnState else None)
            if project.targets_loaded: 
                return
            
            def assign_looks(look:'LookContainer'):
                for d_key in project.dict_looks.keys():
                    if d_key in look.targets_dict:
                        d_list = project.dict_looks[d_key]

                        for look_obj in d_list:
                            if not look_obj.look_active:
                                look_obj.desired_look = d_key
                                self.application.look.add_look(look_obj)

                project.targets_loaded = True

            self.application.look_file.ready(assign_looks)

        self.application.project_ready(lambda p: activate_project)

        self.application.catia.start_command("Apply customized view")
        self.application.catia.refresh_display(True).hso_synchronized(True)


    def load(self) -> 'DomLoadConfig':
        self._filePath = os.path.join(self.application.registry.base_path, self._file_name)

        if not os.path.exists(self._filePath):
            self.application.error_message = f"{self._filePath} not found"
            return self

        self.evaluate_xml(False)
        return self
    
    def open_dialog(self) -> str:
        file_path = filedialog.askopenfilename(
            title="Import variant configuration from .xml",
            filetypes=[("XML Files", "*.xml")],
            initialdir=self.application.registry.base_path
        )
        return file_path

    def clean_variant(self) -> 'DomLoadConfig':
        self.application.project_ready(lambda p: p.variant_ready(lambda v: v.switches.clear() or p.variants.clear()))
        return self

    def import_config(self) -> 'DomLoadConfig':
        self._filePath = self.open_dialog()
        if not self._filePath:
            return self

        if self.application.active_project.variants.count():
            result = messagebox.askyesno("Do you want to add to existing configuration?", "3DExperience configurator | import variant")
            if not result:
                self.clean_variant()

        self.evaluate_xml(True)
        return self

    def finalize(self) -> None:
        self._dictRefs.clear()
        self._dictRefs = None
        self._sel = None
        self._part = None
        self._sets = None
