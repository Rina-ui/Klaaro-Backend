# from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
# import pandas as pd
#
# from app.entities.SecurityQuestionnaire import SecurityQuestionnaire
# from app.use_cases.services.ml.klaaro_ml_service import ml_service
# from app.adapters.dependencies import get_current_user
#
# router = APIRouter(prefix="/ml", tags=["Machine Learning"])
#
# @router.post("/analyse-anomalies")
# async def analyse_anomalies(file: UploadFile = File(...),
#                             current_user = Depends(get_current_user)):
#     try:
#         df = pd.read_csv(file.file)
#         result = ml_service.detect_anomalies(df)
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
#
# @router.post("/explain")
# def explain_data(instruction: str, current_user = Depends(get_current_user)):
#     try:
#         explanation = ml_service.generate_explanation(instruction)
#         return {"explanation": explanation}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
#
# @router.post("/predict")
# async def predict_data(file: UploadFile = File(...), target_col: str = "ventes",
#                        n_days: int = 30, current_user = Depends(get_current_user)):
#     try:
#         df = pd.read_csv(file.file)
#         result = ml_service.predict(df, target_col, n_days)
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
#
# @router.post("/preprocess")
# async def preprocess_data(file: UploadFile = File(...),
#                           current_user = Depends(get_current_user)):
#     try:
#         df = pd.read_csv(file.file)
#         result = ml_service.preprocess_data(df)
#         return {
#             "rapport": result["rapport"],
#             "apercu_donnees": result["data"].head(10).to_dict('records')
#         }
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
#
# @router.post("/security-score")
# def calculate_security(questionnaire: SecurityQuestionnaire,
#                        current_user = Depends(get_current_user)):
#     try:
#         result = ml_service.calculate_security_score(questionnaire.dict())
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from app.entities.SecurityQuestionnaire import SecurityQuestionnaire
from app.adapters.dependencies import get_current_user

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

@router.post("/analyse-anomalies")
async def analyse_anomalies(file: UploadFile = File(...),
                            current_user = Depends(get_current_user)):
    # Simule le retour de ml_service.detect_anomalies(df)
    return {
        "status": "success",
        "anomalies_detectees": 3,
        "indices_anomalies": [14, 45, 82],
        "message": "Analyse terminée. 3 transactions suspectes ont été identifiées dans le fichier envoyé."
    }

@router.post("/explain")
def explain_data(instruction: str, current_user = Depends(get_current_user)):
    # Simule le retour de ml_service.generate_explanation(instruction)
    return {
        "explanation": (
            f"Analyse Klaaro pour l'instruction '{instruction}' :\n\n"
            "Les flux de trésorerie de ce mois montrent une stabilité globale avec une "
            "légère augmentation des charges d'exploitation sur le dernier trimestre. "
            "L'optimisation financière recommandée est de lisser les amortissements pour stabiliser le résultat."
        )
    }

@router.post("/predict")
async def predict_data(file: UploadFile = File(...), target_col: str = "ventes",
                       n_days: int = 30, current_user = Depends(get_current_user)):
    # Simule le retour de ml_service.predict(df, target_col, n_days)
    return {
        "target": target_col,
        "horizon_jours": n_days,
        "prediction_totale": 1550000,
        "tendance": "HAUSSE",
        "confiance": "87%",
        "evolution_estimee": [
            {"jour": 10, "valeur": 510000},
            {"jour": 20, "valeur": 530000},
            {"jour": 30, "valeur": 550000}
        ]
    }

@router.post("/preprocess")
async def preprocess_data(file: UploadFile = File(...),
                          current_user = Depends(get_current_user)):
    # Simule le dictionnaire retourné par ml_service.preprocess_data(df)
    # avec le "rapport" et l'aperçu sous forme de liste de dictionnaires (to_dict('records'))
    return {
        "rapport": {
            "lignes_analysees": 150,
            "colonnes_trouvees": ["date", "description", "montant", "categorie"],
            "valeurs_manquantes_corrigees": 4
        },
        "apercu_donnees": [
            {"date": "2026-07-01", "description": "Achat intrants", "montant": 45000, "categorie": "Charges"},
            {"date": "2026-07-02", "description": "Vente Maïs", "montant": 120000, "categorie": "Produits"},
            {"date": "2026-07-03", "description": "Transport Lomé", "montant": 15000, "categorie": "Charges"}
        ]
    }

@router.post("/security-score")
def calculate_security(questionnaire: SecurityQuestionnaire,
                       current_user = Depends(get_current_user)):
    # Simule le retour de ml_service.calculate_security_score(questionnaire.dict())
    return {
        "score_global": 78,
        "niveau_risque": "FAIBLE",
        "criteres": {
            "securite_physique": "Bonne",
            "gestion_tresorerie": "Moyenne",
            "conformite_legale": "Excellente"
        },
        "recommandations": [
            "Pensez à diversifier vos canaux d'encaissement (Mobile Money / Espèces) pour limiter les risques.",
            "Mettez à jour votre registre des recettes de manière hebdomadaire."
        ]
    }