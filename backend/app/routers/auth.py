"""Routes d'authentification : inscription, connexion, profil."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.auth import (authenticate, create_access_token, get_current_user,
                      hash_password)
from app.database import get_session
from app.models import User
from app.schemas import Token, UserCreate, UserRead

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=201)
def register(payload: UserCreate, session: Session = Depends(get_session)):
    exists = session.exec(select(User).where(User.email == payload.email)).first()
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "E-mail déjà utilisé")
    user = User(email=payload.email, full_name=payload.full_name,
                hashed_password=hash_password(payload.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(),
          session: Session = Depends(get_session)):
    user = authenticate(session, form.username, form.password)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Identifiants incorrects")
    return Token(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserRead)
def me(current: User = Depends(get_current_user)):
    return current
