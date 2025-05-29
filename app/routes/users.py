# Routy pro správu uživatelských účtů
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
import os
from app.database.db import get_session
from app.models.user import User
from app.security.oauth2 import get_current_user
from app.security.auth import get_password_hash

# Vytvoření routeru pro uživatele
router = APIRouter(prefix="/users", tags=["users"])

# Cesta k adresáři šablon
templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
templates = Jinja2Templates(directory=templates_dir)

# Endpoint pro získání profilu přihlášeného uživatele
@router.get("/profile", response_class=HTMLResponse)
async def get_user_profile(request: Request, current_user: User = Depends(get_current_user)):
    """Zobrazí profil přihlášeného uživatele"""
    return templates.TemplateResponse(
        "frontend/profile.html", 
        {"request": request, "user": current_user}
    )

# Endpoint pro úpravu profilu přihlášeného uživatele
@router.post("/profile", response_class=HTMLResponse)
async def update_user_profile(
    request: Request,
    email: str = Form(None),
    full_name: str = Form(None),
    password: str = Form(None),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    db_user = session.get(User, current_user.id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Uživatel nenalezen")
    
    # Aktualizace údajů
    if email:
        # Kontrola, zda email již neexistuje u jiného uživatele
        existing_email = session.exec(
            select(User).where(User.email == email, User.id != current_user.id)
        ).first()
        if existing_email:
            return templates.TemplateResponse(
                "frontend/profile.html", 
                {"request": request, "user": current_user, "error": "Email již existuje"}
            )
        db_user.email = email
    
    if full_name:
        db_user.full_name = full_name
    
    if password:
        db_user.hashed_password = get_password_hash(password)
    
    # Uložení změn do databáze
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    # Vrácení aktualizovaného profilu
    return templates.TemplateResponse(
        "frontend/profile.html", 
        {"request": request, "user": db_user, "success": "Profil byl úspěšně aktualizován"}
    )

# Endpoint pro zobrazení dashboard stránky pro přihlášeného uživatele
@router.get("/dashboard", response_class=HTMLResponse)
async def get_user_dashboard(request: Request, current_user: User = Depends(get_current_user)):
    if current_user.role == "admin":
        return templates.TemplateResponse(
            "admin/dashboard.html", 
            {"request": request, "user": current_user}
        )
    else:
        return templates.TemplateResponse(
            "frontend/dashboard.html", 
            {"request": request, "user": current_user}
        )
