from app.use_cases.repositories.vulnerabilite_repository import VulnerabiliteRepository


class DetectAnomalie():

    def __init__(self, vulnerabilite_repository: VulnerabiliteRepository):
        self.vulnerabilite_repository = vulnerabilite_repository

    def execute(self):
        pass