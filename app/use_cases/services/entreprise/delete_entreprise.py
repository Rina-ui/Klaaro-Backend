from app.use_cases.repositories.entreprise_repository import EntrepriseRepository

class DeleteEntreprise:
    def __init__(self, entreprise_repository: EntrepriseRepository):
        self.entreprise_repository = entreprise_repository

    def execute(self, entreprise_id: str) -> None:
        entreprise = self.entreprise_repository.find_by_id(entreprise_id)
        if not entreprise:
            raise Exception("Entreprise non trouvee")
        self.entreprise_repository.delete_entreprise(entreprise_id)
