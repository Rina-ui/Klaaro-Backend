from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.adapters.dependencies import get_current_user
from app.adapters.schemas.entreprise_schema import EntrepriseResponse, EntrepriseRequest
from app.infrastructure.database import get_db
from app.infrastructure.repositories.entreprise_repository_impl import EntrepriseRepositoryImpl
from app.use_cases.services.entreprise.create_entreprise import CreateEntreprise
from app.use_cases.services.entreprise.find_entreprise_by_id import FindEntrepriseById
from app.use_cases.services.entreprise.delete_entreprise import DeleteEntreprise

router = APIRouter(prefix="/enterprise", tags=["Enterprises"])

@router.post("/", response_model=EntrepriseResponse)
def create_entreprise(request: EntrepriseRequest, db: Session = Depends(get_db),
                      current_user = Depends(get_current_user)):
    try:
        repo = EntrepriseRepositoryImpl(db)
        use_case = CreateEntreprise(repo)
        return use_case.execute(
            name=request.name,
            email=request.email,
            number=request.number,
            location=request.location
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{entreprise_id}", response_model=EntrepriseResponse)
def get_entreprise(entreprise_id: str, db: Session = Depends(get_db),
                   current_user = Depends(get_current_user)):
    try:
        repo = EntrepriseRepositoryImpl(db)
        use_case = FindEntrepriseById(repo)
        return use_case.execute(entreprise_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{entreprise_id}")
def delete_entreprise(entreprise_id: str, db: Session = Depends(get_db),
                      current_user = Depends(get_current_user)):
    try:
        repo = EntrepriseRepositoryImpl(db)
        use_case = DeleteEntreprise(repo)
        use_case.execute(entreprise_id)
        return {"message": "Enterprise deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))