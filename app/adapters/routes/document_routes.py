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
        print("ERREUR UPLOAD BACKEND:", str(e))
        raise HTTPException(status_code=400, detail=str(e))


#On récupère les documents de l'utilisateur connecté via son Token
@router.get("/", response_model=List[DocumentResponse])
def get_user_documents(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        repo = DocumentRepositoryImpl(db)
        # On respecte la Clean Architecture en passant par le Use Case dédié !
        use_case = FindDocumentsByUser(repo)

        documents = use_case.execute(current_user.id)

        if documents is None:
            return []

        return documents
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

@router.get("/stats")
def get_document_stats(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        repo = DocumentRepositoryImpl(db)
        use_case = FindDocumentsByUser(repo)
        documents = use_case.execute(current_user.id) or []

        images = [d for d in documents if d.type == "image"]

        return {
            "uploadedFilesCount": len(documents),
            "uploadedFilesTrend": 0,
            "databaseConnectionsCount": 0,
            "scannedPhotosCount": len(images),
            "scannedPhotosMax": 50,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))