import pytest
import pandas as pd
from app.use_cases.services.ml.klaaro_ml_service import KlaaroMLService

@pytest.fixture
def ml_service():
    """Initialise le service pour chaque test"""
    return KlaaroMLService()

# ----------------------------------------------------------------------
#  TEST 1 : Vérifier que le filtre bloque un CV ou un Mémoire
# ----------------------------------------------------------------------
def test_validate_document_rejects_cv(ml_service):
    # On simule un CV converti en tableau à une colonne textuelle
    data_cv = {
        "texte_brut_pdf": [
            "Curriculum Vitae de Jean Développeur",
            "Compétences: Python, FastAPI, React",
            "Expérience: Stage de fin d'études",
            "Formation: Licence en Informatique"
        ]
    }
    df_cv = pd.DataFrame(data_cv)

    # Exécution de la validation
    validation = ml_service.validate_document_structure(df_cv)

    # Assertions : On s'attend à ce que le document soit rejeté
    assert validation["valid"] is False
    assert "CV" in validation["reason"] or "mémoire" in validation["reason"]

# ----------------------------------------------------------------------
#  TEST 2 : Vérifier qu'un fichier business valide passe sans problème
# ----------------------------------------------------------------------
def test_validate_document_accepts_business_data(ml_service):
    # On simule un fichier de ventes valide
    data_business = {
        "date": ["2026-01-01", "2026-01-02"],
        "article": ["Chaussures", "Chemises"],
        "montant": [25000, 15000],
        "quantite": [2, 1]
    }
    df_business = pd.DataFrame(data_business)

    validation = ml_service.validate_document_structure(df_business)

    assert validation["valid"] is True

# ----------------------------------------------------------------------
#  TEST 3 : Vérifier le nettoyage et l'extraction des Barplots
# ----------------------------------------------------------------------
def test_preprocess_data_cleans_and_returns_chart_data(ml_service):
    # On crée un jeu de données avec des espaces dans les colonnes et des doublons
    data_dirty = {
        "Date Vente ": ["2026-05-01", "2026-05-01", "2026-05-02"], # Doublon sur la ligne 0 et 1
        "Region": ["Maritime", "Maritime", "Plateaux"],
        "Montant": [5000, 5000, 12000]
    }
    df_dirty = pd.DataFrame(data_dirty)

    result = ml_service.preprocess_data(df_dirty)

    assert result["status"] == "success"
    # Vérification du nettoyage de colonnes ("Date Vente " -> "date_vente")
    assert "date_vente" in result["data"].columns
    # Vérification de la suppression de doublon (3 lignes de base -> 2 lignes après nettoyage)
    assert result["rapport"]["lignes_apres"] == 2
    # Vérification des données générées pour le barplot (Top Régions)
    assert len(result["chart_data"]) > 0
    assert result["chart_data"][0]["name"] == "Maritime"

# ----------------------------------------------------------------------
# TEST 4 : Vérifier le calcul du score de sécurité
# ----------------------------------------------------------------------
def test_calculate_security_score_vulnerable(ml_service):
    # On simule un questionnaire catastrophique
    reponses_vulnerables = {
        "mot_de_passe_force": False,
        "mot_de_passe_recent": False,
        "mises_a_jour_actives": False,
        "donnees_chiffrees": False,
        "acces_controles": False,
        "sauvegarde_quotidienne": False
    }

    score_res = ml_service.calculate_security_score(reponses_vulnerables)

    assert score_res["score_total"] == 0
    assert score_res["niveau"] == "Vulnérable"
    assert len(score_res["recommandations"]) > 0