from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from app.database.db import get_session
from app.models.user import User, UserRole
from app.security.auth import authenticate_user, create_user_with_hashed_password
from app.security.oauth2 import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
import os

# Vytvoření routeru pro autentizaci
router = APIRouter(prefix="/auth", tags=["auth"])

# Cesta k adresáři šablon
templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
templates = Jinja2Templates(directory=templates_dir)

# Endpoint pro získání přístupového tokenu
@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    """Endpoint pro přihlášení uživatele a získání JWT tokenu"""
    # Autentizace uživatele pomocí uživatelského jména a hesla
    user = authenticate_user(session, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Neplatné přihlašovací údaje",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Vytvoření JWT tokenu s nastavenou dobou platnosti
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, 
        expires_delta=access_token_expires
    )
    
    # Vrácení tokenu
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint pro zobrazení přihlašovacího formuláře
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Zobrazí stránku s přihlašovacím formulářem"""
    return templates.TemplateResponse(
        "frontend/login.html", {"request": request}
    )

# Endpoint pro zpracování přihlášení pomocí formuláře
@router.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request, username: str = Form(...), password: str = Form(...), session: Session = Depends(get_session)):
    """Zpracování přihlášení uživatele"""
    # Autentizace uživatele
    user = authenticate_user(session, username, password)
    
    if not user:
        # Pokud autentizace selhá, vrátíme zpět na přihlašovací stránku s chybovou zprávou
        return templates.TemplateResponse(
            "frontend/login.html", 
            {"request": request, "error": "Neplatné přihlašovací údaje"}
        )
    
    # Vytvoření JWT tokenu
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, 
        expires_delta=access_token_expires
    )
    
    # Přesměrování na dashboard s tokenem v cookie
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    
    return response

# Endpoint pro zobrazení registračního formuláře
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Zobrazí stránku s registračním formulářem"""
    return templates.TemplateResponse(
        "frontend/register.html", {"request": request}
    )

# Endpoint pro zpracování registrace
@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    """Registrace nového uživatele"""
    # Kontrola, zda uživatelské jméno již neexistuje
    existing_user = session.exec(select(User).where(User.username == username)).first()
    if existing_user:
        return templates.TemplateResponse(
            "frontend/register.html", 
            {"request": request, "error": "Uživatelské jméno již existuje"}
        )
    
    # Kontrola, zda email již neexistuje
    existing_email = session.exec(select(User).where(User.email == email)).first()
    if existing_email:
        return templates.TemplateResponse(
            "frontend/register.html", 
            {"request": request, "error": "Email již existuje"}
        )
    
    # Vytvoření nového uživatele
    user_data = {
        "username": username,
        "email": email,
        "full_name": full_name,
        "password": password,
    }
    
    # Kontrola, zda jde o prvního uživatele v systému - pokud ano, bude to admin
    existing_users_count = session.exec(select(User)).all()
    if not existing_users_count:
        user_data["role"] = UserRole.ADMIN
    
    # Hashování hesla a příprava dat pro databázi
    user_dict = create_user_with_hashed_password(user_data)
    
    # Uložení uživatele do databáze
    new_user = User(**user_dict)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    # Přesměrování na přihlašovací stránku s úspěšnou zprávou
    return templates.TemplateResponse(
        "frontend/login.html", 
        {"request": request, "success": "Registrace byla úspěšná, nyní se můžete přihlásit"}
    )

# Endpoint pro odhlášení
@router.get("/logout")
async def logout():
    """Odhlášení uživatele"""
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    return response
