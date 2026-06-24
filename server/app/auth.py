"""Authentification : JWT + bcrypt."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session, select

from app.config import settings
from app.db import get_session
from app.models import User

oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
_ALG = "HS256"


def hash_pw(pw: str) -> str:
    return bcrypt.hashpw(pw.encode()[:72], bcrypt.gensalt()).decode()


def verify_pw(pw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode()[:72], hashed.encode())
    except ValueError:
        return False


def make_token(sub: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.token_minutes)
    return jwt.encode({"sub": sub, "exp": exp}, settings.secret_key, algorithm=_ALG)


def current_user(token: str = Depends(oauth2),
                 session: Session = Depends(get_session)) -> User:
    exc = HTTPException(status.HTTP_401_UNAUTHORIZED, "Non authentifié",
                        {"WWW-Authenticate": "Bearer"})
    try:
        uid = jwt.decode(token, settings.secret_key, algorithms=[_ALG]).get("sub")
    except JWTError:
        raise exc from None
    user = session.get(User, uid) if uid else None
    if not user:
        raise exc
    return user
