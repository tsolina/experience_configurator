import xml.etree.ElementTree as ET
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from application.xml import XML

class DomSaveLook:
    def __init__(self, parent:'XML'):
        self.application = parent.application
        self._file_name = f"{self.application.active_project.id}_{self.application.active_project.revision}.xml"
        self.x_doc = None
        self.root = None
        self.header = None
        self.product_structure = None
        self._title = None
        self._save_path = ""

    @property
    def file_name(self):
        return self._file_name

    def clear(self):
        self.product_structure = None
        self.header = None
        self.root = None
        self.x_doc = None

    def writter_setup(self):
        # Python's ElementTree automatically formats, but we can set up pretty formatting here if needed
        return self

    def add_processing_instruction(self):
        # ElementTree does not support processing instructions directly, skipping for simplicity
        return self

    def add_root(self):
        self.root = ET.Element("model")
        self.x_doc = ET.ElementTree(self.root)
        return self

    def create_node(self, name:str, parent) -> ET.Element:
        node = ET.SubElement(parent, name.replace(" ", ""))  # Ensure no spaces in element names
        return node

    def create_text(self, text:str, parent:ET.Element):
        if not text:
            return None
        parent.text = text
        return parent

    def add_header(self):
        self.header = self.create_node("header", self.root)
        project = self.application.active_project

        self.create_text(project.name, self.create_node("title", self.header))
        self.create_text(datetime.now().isoformat(), self.create_node("created", self.header))
        self.create_text("Look configurator by TSolina", self.create_node("generator", self.header))
        self.create_text(project.id, self.create_node("id", self.header))
        self.create_text(project.revision, self.create_node("revision", self.header))

        return self

    def add_product_structure(self):
        self.product_structure = self.create_node("lookConfigurator", self.root)
        return self

    def save_default(self):
        self._save_path = f"{self.application.registry.base_path}/{self.file_name}"
        self.x_doc.write(self._save_path, encoding="utf-8", xml_declaration=True)

        self.application.status_message = f"look saved to: {self._save_path}"
        return self

    def config_to_xml(self):
        for config in self.application.active_project.configurations:
            c_node = self.create_node("configuration", self.product_structure)
            self.create_text(config.name, self.create_node("name", c_node))
            self.create_text(config.active_look, self.create_node("look", c_node))
            self.create_text(config.active_look_state, self.create_node("state", c_node))

            c_actors = self.create_node("actors", c_node)
            for actor in config.actors:
                self.create_text(actor.path, self.create_node("actor", c_actors))
        return self

    def prepare_file(self):
        self.x_doc = ET.ElementTree()
        (self.writter_setup()
         .add_processing_instruction()
         .add_root()
         .add_header()
         .add_product_structure()
         .config_to_xml())
        return self

    def save(self):
        self.prepare_file()
        self.save_default()
        self.clear()
        return self

    def save_dialog(self):
        # Python equivalent for file dialog (using tkinter)
        from tkinter.filedialog import asksaveasfilename

        options = {
            "defaultextension": ".xml",
            "filetypes": [("XML Files", "*.xml")],
            "initialdir": self.application.registry.base_path,
            "title": "Export look configuration as .xml",
        }
        return asksaveasfilename(**options)

    def export(self):
        self._save_path = self.save_dialog()
        if not self._save_path:
            return self

        self.prepare_file()
        self.x_doc.write(self._save_path, encoding="utf-8", xml_declaration=True)
        self.clear()

        self.application.status_message = f"look exported as: {self._save_path}"
        return self
