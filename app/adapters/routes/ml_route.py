from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status
import pandas as pd
import io

from pypdf import PdfReader

from app.entities.SecurityQuestionnaire import SecurityQuestionnaire
from app.use_cases.services.ml.klaaro_ml_service import ml_service
from app.adapters.dependencies import get_current_user

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

def _read_file_to_df(file: UploadFile) -> pd.DataFrame:
    """
    Transforme dynamiquement du CSV, Excel, XML ou PDF en DataFrame Pandas standard.
    """
    filename = file.filename.lower()
    contents = file.file.read()
    file.file.seek(0) # Reset le pointeur

    try:
        # GESTION EXCEL
        if filename.endswith(('.xlsx', '.xls')):
            return pd.read_excel(io.BytesIO(contents))

        # GESTION XML
        elif filename.endswith('.xml'):
            # Convertit le XML en liste de dictionnaires automatiquement
            return pd.read_xml(io.BytesIO(contents))

        # GESTION PDF (Extraction textuelle brute pour validation)
        elif filename.endswith('.pdf'):
            reader = PdfReader(io.BytesIO(contents))
            full_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

            if not full_text.strip():
                raise HTTPException(status_code=400, detail="Le fichier PDF est vide ou contient uniquement des images scannées non lisibles.")

            # Pour le PDF, on crée un DataFrame temporaire à une seule colonne de texte.
            # C'est la méthode `validate_document_structure` du service qui va détecter
            # si c'est un CV/Mémoire ou des données d'entreprise structurées.
            lines = [line.strip() for line in full_text.split('\n') if line.strip()]
            return pd.DataFrame(lines, columns=["texte_brut_pdf"])

        # GESTION CSV (Par défaut)
        else:
            try:
                return pd.read_csv(io.BytesIO(contents))
            except UnicodeDecodeError:
                return pd.read_csv(io.BytesIO(contents), encoding='latin-1')

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Impossible de parser le fichier {file.filename}: {str(e)}"
        )

@router.post("/preprocess")
async def preprocess_data(file: UploadFile = File(...),
                          current_user = Depends(get_current_user)):
    try:
        # Transformation magique en DataFrame peu importe le format d'origine !
        df = _read_file_to_df(file)

        # Le service prend le relais pour valider, nettoyer et choisir le graphique
        result = ml_service.preprocess_data(df)

        if result.get("status") == "rejected":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )

        # On retourne exactement les clés calculées par le service blindé
        return {
            "status": "success",
            "format_origine": result.get("format_origine", file.filename.split('.')[-1]),
            "chart_type": result.get("chart_type", "bar"),
            "chart_data": result["chart_data"],
            "rapport": result["rapport"],
            "apercu_donnees": result["apercu_donnees"]
        }
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors du traitement: {str(e)}")

@router.post("/analyse-anomalies")
async def analyse_anomalies(file: UploadFile = File(...),
                            current_user = Depends(get_current_user)):
    try:
        df = _read_file_to_df(file)

        prep = ml_service.preprocess_data(df)
        if prep.get("status") == "rejected":
            raise HTTPException(status_code=400, detail=prep["message"])

        result = ml_service.detect_anomalies(prep.get("data", df))
        return result
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/predict")
async def predict_data(file: UploadFile = File(...), target_col: str = "ventes",
                       n_days: int = 30, current_user = Depends(get_current_user)):
    try:
        df = _read_file_to_df(file)

        # Sécurité : pré-traitement pour standardiser les colonnes (ex: passer de "Ventes" à "ventes")
        prep = ml_service.preprocess_data(df)
        if prep.get("status") == "rejected":
            raise HTTPException(status_code=400, detail=prep["message"])

        result = ml_service.predict(prep["data"], target_col, n_days)
        return result
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/explain")
def explain_data(instruction: str, current_user = Depends(get_current_user)):
    try:
        # =========================================================================
        #  PARTIE TINYLLAMA MISE EN COMMENTAIRE POUR ÉVITER LES SATORATIONS RAM/CPU
        # =========================================================================
        # explanation = ml_service.generate_explanation(instruction)
        # return {"explanation": explanation}
        # =========================================================================

        # Mock temporaire en langage naturel pour le Front-end
        return {
            "explanation": "Mode local activé (TinyLlama désactivé). Analyse des barplots et des prédictions opérationnelle."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/security-score")
def calculate_security(questionnaire: SecurityQuestionnaire,
                       current_user = Depends(get_current_user)):
    try:
        result = ml_service.calculate_security_score(questionnaire.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stats")
async def get_document_stats(current_user = Depends(get_current_user)):
    try:
        # Remplace par ton code réel qui va chercher les documents de l'utilisateur en base
        # Exemple de structure attendue par ton tableau de bord :
        return {
            "uploadedFilesCount": 5,
            "databaseConnectionsCount": 1,
            "globalVolume": 1024,
            "analyses": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))