from datetime import datetime
from typing import Optional, TypeVar, Generic, Type, TYPE_CHECKING
import xml.etree.ElementTree as ET

from application.dom_load_config import DomLoadConfig
from application.dom_load_look import DomLoadLook
from application.dom_save_config import DomSaveConfig
from application.dom_save_look import DomSaveLook

if TYPE_CHECKING:
    from application.application import Application

T = TypeVar('T')  # Generic type for deserialization

class XML():
    def __init__(self, i_parent: 'Application'):
        self._parent: 'Application' = i_parent
        self.application = i_parent
        self._name: str = "XMLHandler"

        # Lazy-loaded properties
        self._save_look: Optional['DomSaveLook'] = None
        self._load_look: Optional['DomLoadLook'] = None
        self._save_config: Optional['DomSaveConfig'] = None
        self._load_config: Optional['DomLoadConfig'] = None
        # self._deltagen_export: Optional['DeltagenExport.CDeltagenExport'] = None
        # self._deltagen_export_look: Optional['DeltagenExport.CDeltaExportLook'] = None

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
    def save_look(self) -> 'DomSaveLook':
        if self._save_look is None:
            self._save_look = DomSaveLook(self)
        return self._save_look

    @save_look.setter
    def save_look(self, value: 'DomSaveLook'):
        self._save_look = value

    @property
    def load_look(self) -> 'DomLoadLook':
        if self._load_look is None:
            self._load_look = DomLoadLook(self)
        return self._load_look

    @load_look.setter
    def load_look(self, value: 'DomLoadLook'):
        self._load_look = value

    @property
    def save_config(self) -> 'DomSaveConfig':
        if self._save_config is None:
            self._save_config = DomSaveConfig(self)
        return self._save_config

    @save_config.setter
    def save_config(self, value: 'DomSaveConfig'):
        self._save_config = value

    @property
    def load_config(self) -> 'DomLoadConfig':
        if self._load_config is None:
            self._load_config = DomLoadConfig(self)
        return self._load_config

    @load_config.setter
    def load_config(self, value: 'DomLoadConfig'):
        self._load_config = value

    # @property
    # def deltagen_export(self) -> 'DeltagenExport.CDeltagenExport':
    #     if self._deltagen_export is None:
    #         self._deltagen_export = DeltagenExport.CDeltagenExport()
    #     return self._deltagen_export

    # @deltagen_export.setter
    # def deltagen_export(self, value: 'DeltagenExport.CDeltagenExport'):
    #     self._deltagen_export = value

    # @property
    # def deltagen_export_look(self) -> 'DeltagenExport.CDeltaExportLook':
    #     if self._deltagen_export_look is None:
    #         self._deltagen_export_look = DeltagenExport.CDeltaExportLook()
    #     return self._deltagen_export_look

    # @deltagen_export_look.setter
    # def deltagen_export_look(self, value: 'DeltagenExport.CDeltaExportLook'):
    #     self._deltagen_export_look = value

    def deserialize_xml_file_to_object(self, xml_filename: str, object_type: Type[T]) -> Optional[T]:
        """
        Deserialize an XML file to an object of type T.
        """
        if not xml_filename:
            return None

        try:
            with open(xml_filename, 'r') as xml_file:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                # Deserialization logic specific to object_type goes here
                # Placeholder: Returning None as actual implementation depends on object_type
                return object_type()  # Example, replace with actual deserialization
        except Exception as ex:
            print(f"Error: {ex} at {datetime.now()}")
            return None
