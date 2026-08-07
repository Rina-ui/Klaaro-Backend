from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from pydantic import BaseModel
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from app.use_cases.services.ml.klaaro_ml_service import ml_service

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp Integration"])

class LinkAccountRequest(BaseModel):
    phone_number: str
    email: str

# 1. Liaison de compte
@router.post("/link-account")
def link_account(payload: LinkAccountRequest):
    # Logique DB : Vérifier l'utilisateur et associer payload.phone_number
    return {"status": "success", "message": f"Votre compte {payload.email} a été lié avec succès à Klaaro !"}

# 2. Q&A Ollama sur les données du Dashboard
@router.get("/ask")
def ask_dashboard(phone_number: str, question: str):
    # Remplace par la récupération réelle des données de l'utilisateur
    context_mock = "Statistiques récentes : 150 documents traités, 3 anomalies détectées, ventes en hausse de 12%."
    prompt = f"Données du dashboard :\n{context_mock}\n\nQuestion de l'utilisateur : {question}"

    answer = ml_service._call_ollama(prompt_context=prompt)
    if not answer:
        answer = "Désolé, je n'ai pas pu analyser vos données pour le moment."
    return {"response": answer}

# 3. Export du fichier nettoyé (CSV / XLSX)
@router.get("/download/processed-file")
def download_processed_file(phone_number: str, file_format: str = "csv"):
    # Exemple avec des données fictives si pas de DF en session
    import pandas as pd
    df_clean = pd.DataFrame({"statut": ["OK", "OK", "Atypiquement élevé"], "valeur": [100, 200, 1500]})

    content, media_type, ext = ml_service.export_processed_file(df_clean, file_format)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename=donnees_nettoyees.{ext}"}
    )

# 4. Génération et export du PDF de prédiction
@router.get("/download/prediction-pdf")
def download_prediction_pdf(phone_number: str, target_col: str = "ventes"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph(f"<b>Rapport de Prédiction : {target_col.upper()}</b>", styles['Title']))
    elements.append(Spacer(1, 12))

    explanation = ml_service._call_ollama(f"Explique brièvement des prévisions à la hausse pour {target_col}.")
    elements.append(Paragraph("<b>Résumé des prévisions :</b>", styles['Heading2']))
    elements.append(Paragraph(explanation or "Analyse basée sur les tendances historiques.", styles['Normal']))
    elements.append(Spacer(1, 18))

    # Tableau de prédictions
    data = [["Période", "Valeur Prédite"], ["Jour +1", "120.5"], ["Jour +2", "125.0"], ["Jour +3", "131.2"]]
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
    ]))
    elements.append(t)

    doc.build(elements)
    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=rapport_prediction.pdf"}
    )