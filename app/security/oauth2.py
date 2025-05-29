from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlmodel import Session, select
from app.database.db import get_session
from app.models.user import User

# Tajný klíč pro JWT token - měl by být v prostředí proměnných v produkčním prostředí
SECRET_KEY = "tajny_klic_pro_jwt_token_ktery_by_mel_byt_v_prostredi_promennych"
ALGORITHM = "HS256"
# Doba platnosti tokenu (30 minut)
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Endpoint pro autentizaci
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
# Model pro data uložená v tokenu
class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

# Vytvoření JWT tokenu
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Vytvoří nový JWT token s předanou dobou platnosti"""
    to_encode = data.copy()
    
    # Nastavení doby platnosti tokenu
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    # Vytvoření JWT tokenu
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Ověření uživatele pomocí JWT tokenu
async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    """Získá aktuálního přihlášeného uživatele z JWT tokenu"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Neplatné přihlašovací údaje",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Dekódování JWT tokenu
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        token_data = TokenData(username=username, role=payload.get("role"))
    except JWTError:
        raise credentials_exception
    
    # Získání uživatele z databáze
    statement = select(User).where(User.username == token_data.username)
    user = session.exec(statement).first()
    
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Uživatel není aktivní"
        )
    
    return user

# Ověření, zda je uživatel administrátor
async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """Ověří, zda je přihlášený uživatel administrátor"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nedostatečná práva pro přístup"
        )
    return current_user
