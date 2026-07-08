from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.adapters.dependencies import get_current_user
from app.adapters.schemas.document_schema import DocumentResponse, DocumentRequest
from app.infrastructure.database import get_db
from app.infrastructure.repositories.document_repository_impl import DocumentRepositoryImpl
from app.use_cases.services.document.create_document import CreateDocument
from app.use_cases.services.document.delete_document import DeleteDocument
from app.use_cases.services.document.find_documents_by_user import FindDocumentsByUser

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

@router.post("/", response_model=DocumentResponse)
def create_document(request: DocumentRequest, db: Session = Depends(get_db),
                    current_user = Depends(get_current_user)):
    try:
        repo = DocumentRepositoryImpl(db)
        use_case = CreateDocument(repo)
        return use_case.execute(
            name=request.name,
            type=request.type,
            taille=request.taille,
            content=request.content,
            user_id=current_user.id,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=List[DocumentResponse])
def get_document(user_id: str, db: Session = Depends(get_db),
                 current_user = Depends(get_current_user)):
    try:
        repo = DocumentRepositoryImpl(db)
        use_case = FindDocumentsByUser(repo)
        return use_case.execute(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db),
                    current_user = Depends(get_current_user)):
    try:
        repo = DocumentRepositoryImpl(db)
        use_case = DeleteDocument(repo)
        use_case.execute(document_id)
        return {"message": "Document successfully deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))