from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query, status
from fastapi.responses import StreamingResponse
import pandas as pd
import io
import json
import pdfplumber
from pypdf import PdfReader

from app.entities.SecurityQuestionnaire import SecurityQuestionnaire
from app.use_cases.services.ml.klaaro_ml_service import ml_service
from app.adapters.dependencies import get_current_user

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

def _read_file_to_df(file: UploadFile) -> pd.DataFrame:
    """Transforme dynamiquement du CSV, Excel, JSON, XML ou PDF en DataFrame Pandas standard."""
    filename = file.filename.lower()
    contents = file.file.read()
    file.file.seek(0)  # Reset du pointeur

    try:
        # 1. GESTION EXCEL (.xlsx, .xls)
        if filename.endswith((".xlsx", ".xls")):
            return pd.read_excel(io.BytesIO(contents))

        # 2. GESTION JSON (.json)
        elif filename.endswith(".json"):
            data = json.loads(contents.decode("utf-8"))
            if isinstance(data, list):
                return pd.DataFrame(data)
            elif isinstance(data, dict):
                # On cherche la première clé qui contient une liste de données
                for key, val in data.items():
                    if isinstance(val, list):
                        return pd.DataFrame(val)
                return pd.DataFrame([data])
            else:
                raise HTTPException(
                    status_code=400, detail="Structure JSON non valide."
                )

        # 3. GESTION XML (.xml)
        elif filename.endswith(".xml"):
            return pd.read_xml(io.BytesIO(contents))

        # 4. GESTION PDF (.pdf) -> Extraction de Tableaux Métiers
        elif filename.endswith(".pdf"):
            tables = []
            # Essai avec pdfplumber pour extraire de vrais tableaux (ventes, stocks...)
            with pdfplumber.open(io.BytesIO(contents)) as pdf:
                for page in pdf.pages:
                    extracted_table = page.extract_table()
                    if extracted_table:
                        tables.extend(extracted_table)

            if tables and len(tables) > 1:
                # La première ligne contient les en-têtes
                df_pdf = pd.DataFrame(tables[1:], columns=tables[0])
                # Nettoyage des None éventuels créés par l'extraction
                return df_pdf.dropna(how="all")

            # Fallback si aucun tableau structuré n'a été détecté (Texte brut)
            reader = PdfReader(io.BytesIO(contents))
            full_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

            if not full_text.strip():
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Le fichier PDF est vide ou contient uniquement des images"
                        " scannées."
                    ),
                )

            lines = [
                line.strip() for line in full_text.split("\n") if len(line.strip()) > 3
            ]
            return pd.DataFrame(lines, columns=["texte_brut_pdf"])

        # 5. GESTION CSV (.csv et autres)
        else:
            try:
                return pd.read_csv(io.BytesIO(contents))
            except UnicodeDecodeError:
                return pd.read_csv(io.BytesIO(contents), encoding="latin-1")

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Impossible de parser le fichier {file.filename}: {str(e)}",
        )

@router.post("/preprocess")
async def preprocess_data(file: UploadFile = File(...),
                          current_user = Depends(get_current_user)):
    try:
        df = _read_file_to_df(file)
        result = ml_service.preprocess_data(df)

        if result.get("status") == "rejected":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )

        return {
            "status": "success",
            "format_origine": result.get("format_origine", file.filename.split('.')[-1]),
            "charts": result["charts"], # Contient la liste des graphiques avec titres, motifs et explications faciles
            "rapport": result["rapport"],
            "apercu_donnees": result["apercu_donnees"]
        }
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors du traitement: {str(e)}")

@router.post("/export")
async def export_processed_data(
        file: UploadFile = File(...),
        export_format: str = Query("csv", enum=["csv", "xlsx", "json"]),
        current_user = Depends(get_current_user)
):
    """
    Nettoie le fichier soumis et renvoie le fichier transformé au format désiré (csv, xlsx, json).
    """
    try:
        df = _read_file_to_df(file)

        # 1. Traitement et nettoyage des données
        prep = ml_service.preprocess_data(df)
        if prep.get("status") == "rejected":
            raise HTTPException(status_code=400, detail=prep["message"])

        cleaned_df = prep.get("data")
        if cleaned_df is None or cleaned_df.empty:
            raise HTTPException(status_code=400, detail="Aucune donnée exploitable à exporter.")

        # 2. Génération du buffer binaire
        file_bytes, media_type, ext = ml_service.export_processed_file(cleaned_df, file_format=export_format)

        # 3. Nom du fichier téléchargé
        original_base_name = file.filename.rsplit('.', 1)[0]
        download_filename = f"{original_base_name}_clean.{ext}"

        # 4. Envoi du fichier en StreamingResponse
        return StreamingResponse(
            io.BytesIO(file_bytes),
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{download_filename}"',
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors de l'exportation: {str(e)}")

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