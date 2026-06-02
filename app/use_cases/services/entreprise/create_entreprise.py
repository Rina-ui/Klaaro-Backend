import uuid
from datetime import datetime
from app.entities.entreprise import Entreprise
from app.use_cases.repositories.entreprise_repository import EntrepriseRepository

class CreateEntreprise:
    def __init__(self, entreprise_repository: EntrepriseRepository):
        self.entreprise_repository = entreprise_repository

    def execute(self, name: str, email: str, number: str, location: str) -> Entreprise:
        entreprise = Entreprise(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            number=number,
            location=location,
            creation_date=datetime.utcnow()
        )
        return self.entreprise_repository.save_entreprise(entreprise)
