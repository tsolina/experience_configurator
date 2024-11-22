import os
import xml.etree.ElementTree as ET
from tkinter import filedialog
import tkinter as tk
import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from application.xml import XML
    from application.application import Application

class DomSaveConfig:
    def __init__(self, parent:'XML'):
        self.application = parent.application
        self._save_path = r"C:\Users\tomislav.solina\Desktop\3dx\viz"
        self.XDoc:ET.ElementTree = None
        self.Root = None
        self.Header = None
        self.ProductStructure = None
        self._title = None

    @property
    def _file_name(self):
        return f"cfg_{self.application.active_project.id}.xml"

    def clear(self):
        self.ProductStructure = None
        self.Header = None
        self.Root = None
        self.XDoc = None

    def writter_setup(self):
        writter_settings = ET.ElementTree()
        # You can adjust the settings later for indenting or other XML configurations
        return self

    def add_processing_instruction(self):
        # XML declaration is already handled by ElementTree, so we don’t need explicit instructions here
        return self

    def add_root(self):
        self.Root = ET.Element("model")
        self.XDoc.append(self.Root)
        return self

    def create_node(self, iName: str, iParent: ET.Element):
        if ' ' in iName:
            iName = iName.replace(' ', '')
        node = ET.SubElement(iParent, iName)
        return node

    def create_text(self, iText: str, iParent: ET.Element):
        if iText == "":
            return None
        text_node = ET.SubElement(iParent, "text")
        text_node.text = iText
        return text_node

    def add_header(self):
        self.Header = self.create_node("header", self.Root)

        self.create_text(self.application.active_project.id, self.Header)
        self._title = self.create_text(self.application.active_project.name, self.Header)
        self.create_text(str(datetime.datetime.now()), self.Header)
        self.create_text("Configurator by TSolina", self.Header)

        return self

    def add_product_structure(self):
        self.ProductStructure = self.create_node("configurator", self.Root)
        return self

    def config_to_xml(self):
        for v in self.application.active_project.variants.variant_collection:
            v_node = self.create_node("variant", self.ProductStructure)
            self.create_text(v.name, v_node)
            self.create_text(v.active_state, v_node)

            for sv in v.sub_variants.sub_variant_collection:
                if not sv.switches:
                    continue

                sv_node = self.create_node("state", v_node)
                self.create_text(sv.name, sv_node)

                v_switches = self.create_node("switches", sv_node)
                for s in sv.switches.switch_collection:
                    s_node = self.create_node("switch", v_switches)
                    self.create_text(s.type_, s_node)
                    self.create_text(s.name, s_node)
                    self.create_text(s.active_value, s_node)

        return self

    def prepare_file(self):
        self.Root = ET.Element("model")  # Create the root element first
        self.XDoc = ET.ElementTree(self.Root)  # Now create the ElementTree with the root
        self.writter_setup().add_processing_instruction().add_root().add_header().add_product_structure().config_to_xml()
        return self

    def save(self):
        self.prepare_file()

        self._save_path = os.path.join(self.application.registry.base_path, self._file_name)
        try:
            self.XDoc.write(self._save_path)
            self.application.status_message = f"variant configuration saved to: {self._save_path}"
        except Exception as ex:
            self.application.error_message = str(ex)

        self.clear()
        return self

    def save_dialog(self):
        save_path = ""
        filetypes = [("XML Files", "*.xml")]
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xml", filetypes=filetypes,
            initialdir=self.application.registry.base_path, title="Export variant configuration as .xml",
            initialfile=self._file_name)

        return save_path

    def export(self):
        self._save_path = self.save_dialog()
        if not self._save_path:
            return self

        self.prepare_file()
        self.XDoc.write(self._save_path)
        self.clear()
        self.application.status_message = f"variant configuration exported as: {self._save_path}"

        return self
