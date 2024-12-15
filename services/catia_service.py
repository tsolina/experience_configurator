import experience as exp

class CatiaService:
    def __init__(self, catia_com):
        self.catia_com = catia_com
        self.catia: exp.Application = exp.Application(catia_com) if catia_com else exp.experience_application()