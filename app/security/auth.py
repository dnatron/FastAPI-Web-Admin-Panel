# Autentizace a hashování hesel
from passlib.context import CryptContext
from sqlmodel import Session, select
from app.models.user import User
from typing import Optional
from fastapi import HTTPException, status

# Kontext pro hashování hesel
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Ověření hesla
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Ověří, zda zadané heslo odpovídá hashovanému heslu"""
    return pwd_context.verify(plain_password, hashed_password)

# Hashování hesla
def get_password_hash(password: str) -> str:
    """Vytvoří hash hesla pomocí bcrypt algoritmu"""
    return pwd_context.hash(password)

# Autentizace uživatele
def authenticate_user(session: Session, username: str, password: str) -> Optional[User]:
    """Autentizuje uživatele podle uživatelského jména a hesla"""
    # Hledáme uživatele podle uživatelského jména
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    
    # Pokud uživatel neexistuje nebo heslo neodpovídá, vrátíme None
    if not user or not verify_password(password, user.hashed_password):
        return None
    
    # Pokud uživatel není aktivní, vyhodil bychom výjimku
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Uživatel není aktivní"
        )
    
    return user

# Vytvoření nového uživatele s hashovaným heslem
def create_user_with_hashed_password(user_dict: dict) -> dict:
    """Připraví slovník pro vytvoření uživatele s hashovaným heslem"""
    # Ověření, že heslo existuje
    if "password" not in user_dict:
        raise ValueError("Heslo je povinné pro vytvoření uživatele")
    
    # Získání a odstranění hesla ze slovníku
    password = user_dict.pop("password")
    
    # Přidání hashovaného hesla do slovníku
    user_dict["hashed_password"] = get_password_hash(password)
    
    return user_dict
