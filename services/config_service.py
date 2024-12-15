from application.application import Application


class ConfigService:
    def __init__(self, application:'Application'):
        self.application = application