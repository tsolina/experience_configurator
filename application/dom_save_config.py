import os
import xml.etree.ElementTree as ET
from tkinter import filedialog
import tkinter as tk
import datetime
from typing import TYPE_CHECKING, Optional, Union, overload

if TYPE_CHECKING:
    from application.xml import XML
    from application.application import Application

class DomSaveConfig:
    def __init__(self, parent:'XML'):
        self.application = parent.application
        # self._save_path = r"C:\Users\tomislav.solina\Desktop\3dx\viz"
        self._save_path = r"C:\temp"
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

    # def add_root(self):
    #     self.Root = ET.Element("model")
    #     self.XDoc.append(self.Root)
    #     return self
    def add_root(self):
        self.Root = ET.Element("model")  # Create the root element
        self.XDoc._setroot(self.Root)  # Set it as the root of the ElementTree
        return self

    def create_node(self, iName: str, iParent: ET.Element):
        if ' ' in iName:
            iName = iName.replace(' ', '')
        node = ET.SubElement(iParent, iName)
        return node
    


    # def create_text(self, iText: str, iParent: ET.Element):
    #     if iText == "":
    #         return None
    #     text_node = ET.SubElement(iParent, "text")
    #     text_node.text = iText
    #     return text_node
    # @overload
    # def create_text(self, text: str, parent: ET.Element) -> Optional[ET.Element]:
    #     ...

    # @overload
    # def create_text(self, node_name: str, parent: ET.Element, text: str) -> Optional[ET.Element]:
    #     ...

    # def create_text(self, 
    #                 arg1: Union[str, ET.Element], 
    #                 arg2: Union[ET.Element, str], 
    #                 text: Optional[str] = None) -> Optional[ET.Element]:
    #     """
    #     Creates a text node under the given parent or nested within a newly created child node.

    #     Args:
    #         arg1: Either the text to add or the name of the child node to create.
    #         arg2: The parent element or text to add.
    #         text: Optional text content for the new node.

    #     Returns:
    #         Optional[ET.Element]: The created text node, or None if the text is empty.
    #     """
    #     if text is None:
    #         # Case: create_text(text, parent)
    #         iText, iParent = arg1, arg2
    #     else:
    #         # Case: create_text(node_name, parent, text)
    #         iNodeName, iParent, iText = arg1, arg2, text
    #         iParent = self.create_node(iNodeName, iParent)

    #     if not iText.strip():  # Ignore empty or whitespace-only text
    #         return None

    #     # Create text node
    #     text_node = ET.SubElement(iParent, "text")
    #     text_node.text = iText
    #     return text_node

    def create_text_node(self, name:str, parent, text:str):
        text_node = ET.SubElement(parent, name)
        text_node.text = text
        return text_node


    # def add_header(self):
    #     self.Header = self.create_node("header", self.Root)

    #     self.create_text(self.application.active_project.id, self.Header)
    #     self._title = self.create_text(self.application.active_project.name, self.Header)
    #     self.create_text(str(datetime.datetime.now()), self.Header)
    #     self.create_text("Configurator by TSolina", self.Header)

    #     return self
    def add_header(self) -> "DomSaveConfig":
        """
        Adds a header node to the XML document with predefined child elements.

        Returns:
            DomSaveConfig: The instance of the class for method chaining.
        """
        self.Header = self.create_node("header", self.Root)

        # Adding child nodes with text content
        # self.create_text("id", self.Header, self.application.active_project.id)
        # self._title = self.create_text("title", self.Header, self.application.active_project.name)
        # self.create_text("created", self.Header, str(datetime.datetime.now()))
        # self.create_text("generator", self.Header, "Configurator by TSolina")
        
        self.create_text_node("id", self.Header, self.application.active_project.id)
        self._title = self.create_text_node("title", self.Header, self.application.active_project.name)
        self.create_text_node("created", self.Header, str(datetime.datetime.now()))
        self.create_text_node("generator", self.Header, "Configurator by TSolina")
        

        return self

    def add_product_structure(self):
        self.ProductStructure = self.create_node("configurator", self.Root)
        return self

    def config_to_xml(self):
        for v in self.application.active_project.variants:
            v_node = self.create_node("variant", self.ProductStructure)
            self.create_text_node("name", v_node, v.name)
            self.create_text_node('activeState', v_node, v.active_state.strip())

            for sv in v.sub_variants:
                if not sv.switches:
                    continue

                sv_node = self.create_node("state", v_node)
                self.create_text_node("value", sv_node, sv.name.strip())

                v_switches = self.create_node("switches", sv_node)
                for s in sv.switches:
                    s_node = self.create_node("switch", v_switches)
                    self.create_text_node("type", s_node, s.type_.name)
                    self.create_text_node("actor", s_node, s.name)
                    self.create_text_node("value", s_node, s.active_value)

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
