from application.application import Application
from services.catia_service import CatiaService
from services.config_service import ConfigService
from services.look_service import LookService
from services.project_service import ProjectService
from services.status_service import StatusService


class Services:
    def __init__(self, application:'Application', catia_com=None):
        self.application = application
        self.look = LookService(application)
        self.config = ConfigService(application)
        self.status = StatusService()
        self.project = ProjectService(application)
        self.catia = CatiaService(catia_com)