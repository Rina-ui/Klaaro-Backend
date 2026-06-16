from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from app.use_cases.services.ocr.ocr_service import ocr_service
from app.adapters.dependencies import get_current_user
import shutil
import os
import uuid

router = APIRouter(prefix="/ocr", tags=["OCR"])

@router.post("/extract")
async def extract_from_image(file: UploadFile = File(...),
                             current_user = Depends(get_current_user)):
    try:
        os.makedirs("uploads/temp", exist_ok=True)
        temp_path = f"uploads/temp/{uuid.uuid4()}_{file.filename}"

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = ocr_service.extract_structured_data(temp_path)

        os.remove(temp_path)

        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))