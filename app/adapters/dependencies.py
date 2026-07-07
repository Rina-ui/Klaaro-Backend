from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import os

from app.infrastructure.database import get_db
from app.infrastructure.repositories.user_repository_impl import UserRepositoryImpl

SECRET_KEY = os.getenv("SECRET_KEY", "klaaro_secret_key")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token invalide")
        repo = UserRepositoryImpl(db)
        user = repo.find_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="Utilisateur non trouve")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide ou expire")