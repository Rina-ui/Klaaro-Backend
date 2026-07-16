# app/services/vulnerabilite_service.py
import re
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.infrastructure.models.vulnerabilite_model import VulnerabiliteModel
from app.entities.enum.NiveauVul import NiveauVul
from app.entities.enum.Status import Status
from app.entities.enum.typeVulnerabilite import TypeVulnerabilite

class VulnerabiliteService:
    def __init__(self, db: Session):
        self.db = db

    def analyser_document(self, user_id: str, document_name: str, document_content: str) -> list[VulnerabiliteModel]:
        """
        Analyse le contenu d'un document textuel à la recherche de failles de sécurité
        et enregistre les vulnérabilités trouvées en base de données.
        """
        vulns_detectees = []

        if not document_content:
            return vulns_detectees

        # 1. Recherche de secrets / mots de passe en clair (Exemple de détection)
        # Regex cherchant des motifs comme password = "..." ou api_key : '...'
        secret_patterns = [
            (r"(?i)(password|passwd|pwd|mot_de_passe)\s*[:=]\s*['\"]([^'\"]+)['\"]", "Mot de passe en clair détecté"),
            (r"(?i)(api_key|apikey|secret_key|private_key)\s*[:=]\s*['\"]([^'\"]+)['\"]", "Clé d'API ou clé privée exposée")
        ]

        for pattern, message_template in secret_patterns:
            matches = re.findall(pattern, document_content)
            for match in matches:
                cle, valeur = match
                # On évite de lever une alerte sur des valeurs de test vides ou génériques
                if len(valeur.strip()) > 3 and valeur.lower() not in ["test", "null", "none", "password"]:
                    description = f"Dans le fichier '{document_name}' : {message_template} ('{cle}')."

                    vuln = VulnerabiliteModel(
                        id=str(uuid.uuid4()),
                        type=TypeVulnerabilite.DONNEES_EXPOSEES, # Adapte selon tes enums dispo
                        niveau=NiveauVul.Critique,
                        description=description,
                        status=Status.SUGGEREE,
                        date_detected=datetime.now(),
                        user_id=user_id
                    )
                    vulns_detectees.append(vuln)

        # 2. Recherche d'emails ou données personnelles massives non protégées (Exemple RGPD)
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        emails_trouves = re.findall(email_pattern, document_content)
        if len(emails_trouves) > 5: # Seuil arbitraire pour détecter un dump de données clients
            description = f"Le fichier '{document_name}' contient une liste importante d'adresses email ({len(emails_trouves)} trouvées) non chiffrées ou non anonymisées."

            vuln = VulnerabiliteModel(
                id=str(uuid.uuid4()),
                type=TypeVulnerabilite.DONNEES_EXPOSEES,
                niveau=NiveauVul.Moyenne,
                description=description,
                status=Status.SUGGEREE,
                date_detected=datetime.now(),
                user_id=user_id
            )
            vulns_detectees.append(vuln)

        # Enregistrement en base de données si des failles ont été trouvées
        if vulns_detectees:
            self.db.add_all(vulns_detectees)
            self.db.commit()
            print(f"[CyberSec] {len(vulns_detectees)} vulnérabilité(s) détectée(s) pour l'utilisateur {user_id}")
            for v in vulns_detectees:
                self.db.refresh(v)

        return vulns_detectees