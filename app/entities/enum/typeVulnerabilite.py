from enum import Enum

class TypeVulnerabilite(Enum):
    DONNEES_EXPOSEES = "donnees_exposees"
    ACCES_NON_AUTORISE = "acces_non_autorise"
    FUITE_DONNEES = "fuite_donnees"
    INJECTION = "injection"