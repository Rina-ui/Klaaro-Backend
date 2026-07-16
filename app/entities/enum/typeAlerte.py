from enum import Enum

class TypeAlerte(Enum):
    ANOMALIE_VENTES = "anomalie_ventes"
    ANOMALIE_FINANCIERE = "anomalie_financiere"
    ACCES_SUSPECT = "acces_suspect"
    PIC_DONNEES = "pic_donnees"
    SECURITY = "security"
    ANOMALIE = "anomalie"
    PREDICTION = "prediction"