import uuid
from datetime import datetime
from app.entities.entreprise import Entreprise
from app.use_cases.repositories.entreprise_repository import EntrepriseRepository
from app.use_cases.repositories.user_repository import UserRepository

class CreateEntreprise:
    def __init__(self, entreprise_repository: EntrepriseRepository, user_repository: UserRepository):
        self.entreprise_repository = entreprise_repository
        self.user_repository = user_repository

    def execute(self, name: str, email: str, number: str, location: str, user_id: str) -> Entreprise:
        # Créer l'entreprise
        entreprise = Entreprise(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            number=number,
            location=location,
            creation_date=datetime.utcnow()
        )
        saved_entreprise = self.entreprise_repository.save_entreprise(entreprise)

        # Associer l'entreprise à l'utilisateur qui l'a créée
        user = self.user_repository.get_user_by_id(user_id)
        if user:
            user.entreprise_id = saved_entreprise.id
            user.role = "admin"
            self.user_repository.update_user(user)

        return saved_entreprise