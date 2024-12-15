from application.application import Application
from services.catia_service import CatiaService
from services.config_service import ConfigService
from services.look_service import LookService
from services.project_service import ProjectService
from services.status_service import StatusService
from services.utility import Utility


class Services:
    def __init__(self, application:'Application', catia_com=None):
        self.application = application
        self.status = StatusService()        
        self.utility = Utility()
        self.catia = CatiaService(catia_com)
        self.config = ConfigService(application)
        self.look = LookService(application)
        self.project = ProjectService(application)

        