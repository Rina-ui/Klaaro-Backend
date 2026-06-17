from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.use_cases.services.ml.klaaro_ml_service import ml_service

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

class IncomingMessage(BaseModel):
    from_: str
    message: str

    class Config:
        fields = {'from_': 'from'}

@router.post("/message")
def receive_message(payload: dict):
    try:
        from_number = payload.get("from")
        message = payload.get("message")

        if not message:
            return {"reply": "Je n'ai pas compris votre message. Pouvez-vous reformuler ?"}

        # Generer une explication via le LLM
        reply = ml_service.generate_explanation(message)

        return {"reply": reply}
    except Exception as e:
        return {"reply": "Une erreur s'est produite. Reessayez plus tard."}