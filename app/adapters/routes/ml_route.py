from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
import pandas as pd
from app.use_cases.services.ml.klaaro_ml_service import ml_service
from app.adapters.dependencies import get_current_user

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

@router.post("/analyse-anomalies")
async def analyse_anomalies(file: UploadFile = File(...),
                            current_user = Depends(get_current_user)):
    try:
        df = pd.read_csv(file.file)
        result = ml_service.detect_anomalies(df)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/explain")
def explain_data(instruction: str, current_user = Depends(get_current_user)):
    try:
        explanation = ml_service.generate_explanation(instruction)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/predict")
async def predict_data(file: UploadFile = File(...), target_col: str = "ventes",
                       n_days: int = 30, current_user = Depends(get_current_user)):
    try:
        df = pd.read_csv(file.file)
        result = ml_service.predict(df, target_col, n_days)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/preprocess")
async def preprocess_data(file: UploadFile = File(...),
                          current_user = Depends(get_current_user)):
    try:
        df = pd.read_csv(file.file)
        result = ml_service.preprocess_data(df)
        return {
            "rapport": result["rapport"],
            "apercu_donnees": result["data"].head(10).to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))