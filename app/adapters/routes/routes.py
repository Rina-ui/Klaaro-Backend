from app.adapters.routes.user_routes import router as user_router
from app.adapters.routes.decision_routes import router as decision_router
from app.adapters.routes.vulnerabilite_routes import router as vulnerability_router
from app.adapters.routes.requete_routes import router as requeste_router
from app.adapters.routes.rapport_routes import router as rapport_router
from app.adapters.routes.reponse_routes import router as response_router
from app.adapters.routes.enteprise_routes import router as entreprise_router
from app.adapters.routes.document_routes import router as document_router
from app.adapters.routes.alerte_routes import router as alert_router
from app.adapters.routes.ml_route import router as ml_router
from app.adapters.routes.ocr_route import router as ocr_router

from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(user_router)
api_router.include_router(decision_router)
api_router.include_router(vulnerability_router)
api_router.include_router(alert_router)
api_router.include_router(document_router)
api_router.include_router(entreprise_router)
api_router.include_router(rapport_router)
api_router.include_router(requeste_router)
api_router.include_router(response_router)
api_router.include_router(ml_router)
api_router.include_router(ocr_router)