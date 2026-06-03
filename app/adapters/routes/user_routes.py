from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app.adapters.schemas.user_schema import UserResponse, UserRequest, LoginResponse, LoginRequest
from app.infrastructure.database import get_db
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from app.use_cases.services.user.authenticate_user import AuthenticateUser
from app.use_cases.services.user.create_user import CreateUser
from app.use_cases.services.user.delete_user import DeleteUser
from app.use_cases.services.user.find_user_by_id import FindUserById

router = APIRouter(prefix="/user", tags=["User"])

@router.post("/register", response_model=UserResponse)
def register(request: UserRequest, db: Session = Depends(get_db)):
    try:
        repo = UserRepositoryImpl(db)
        use_case = CreateUser(repo)
        return use_case.execute(
            firstname=request.firstname,
            lastname=request.lastname,
            email=request.email,
            password=request.password,
            profession=request.profession,
            role=request.role,
            account_type=request.account_type
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        repo = UserRepositoryImpl(db)
        use_case = AuthenticateUser(repo)
        return use_case.execute(
            email=request.email,
            password=request.password
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    try:
        repo = UserRepositoryImpl(db)
        use_case = FindUserById(repo)
        return use_case.execute(user_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{user_id}", response_model=UserResponse)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    try:
        repo = UserRepositoryImpl(db)
        use_case = DeleteUser(repo)
        use_case.execute(user_id)
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))