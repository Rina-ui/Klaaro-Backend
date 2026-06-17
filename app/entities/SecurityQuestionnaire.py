from pydantic import BaseModel

class SecurityQuestionnaire(BaseModel):
    mot_de_passe_force: bool
    mot_de_passe_recent: bool
    mises_a_jour_actives: bool
    donnees_chiffrees: bool
    acces_controles: bool
    sauvegarde_quotidienne: bool