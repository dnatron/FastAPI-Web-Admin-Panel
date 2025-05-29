from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
import os
from app.database.db import get_session
from app.models.user import User, UserRole
from app.security.oauth2 import get_current_admin_user
from app.security.auth import create_user_with_hashed_password

# Vytvoření routeru pro administrátorské operace
router = APIRouter(prefix="/admin", tags=["admin"])

# Cesta k adresáři šablon
templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
templates = Jinja2Templates(directory=templates_dir)

# Endpoint pro získání seznamu všech uživatelů (pouze pro adminy)
@router.get("/users", response_class=HTMLResponse)
async def list_users(request: Request, current_user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    # Získání všech uživatelů z databáze
    statement = select(User)
    users = session.exec(statement).all()
    
    return templates.TemplateResponse(
        "admin/users.html", 
        {"request": request, "users": users, "current_user": current_user}
    )

# Endpoint pro vytvoření nového uživatele administrátorem
@router.post("/users/create", response_class=HTMLResponse)
async def create_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    current_user: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """Vytvoří nového uživatele administrátorem"""
    # Kontrola, zda uživatelské jméno již neexistuje
    existing_user = session.exec(select(User).where(User.username == username)).first()
    if existing_user:
        users = session.exec(select(User)).all()
        return templates.TemplateResponse(
            "admin/users.html", 
            {
                "request": request, 
                "users": users, 
                "current_user": current_user, 
                "error": "Uživatelské jméno již existuje"
            }
        )
    
    # Kontrola, zda email již neexistuje
    existing_email = session.exec(select(User).where(User.email == email)).first()
    if existing_email:
        users = session.exec(select(User)).all()
        return templates.TemplateResponse(
            "admin/users.html", 
            {
                "request": request, 
                "users": users, 
                "current_user": current_user, 
                "error": "Email již existuje"
            }
        )
    
    # Ověření, zda je role platná
    try:
        user_role = UserRole(role)
    except ValueError:
        users = session.exec(select(User)).all()
        return templates.TemplateResponse(
            "admin/users.html", 
            {
                "request": request, 
                "users": users, 
                "current_user": current_user, 
                "error": "Neplatná role uživatele"
            }
        )
    
    # Vytvoření nového uživatele
    user_data = {
        "username": username,
        "email": email,
        "full_name": full_name,
        "password": password,
        "role": user_role
    }
    
    # Hashování hesla a příprava dat pro databázi
    user_dict = create_user_with_hashed_password(user_data)
    
    new_user = User(**user_dict)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return RedirectResponse(
        url="/admin/users",
        status_code=status.HTTP_303_SEE_OTHER
    )

# Endpoint pro úpravu uživatele administrátorem
@router.post("/users/{user_id}/edit", response_class=HTMLResponse)
async def update_user(
    user_id: int,
    request: Request,
    email: str = Form(None),
    full_name: str = Form(None),
    password: str = Form(None),
    role: str = Form(None),
    is_active: bool = Form(None),
    current_user: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):

    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Uživatel nenalezen")
    
    # Aktualizace údajů
    if email:
        # Kontrola, zda email již neexistuje u jiného uživatele
        existing_email = session.exec(
            select(User).where(User.email == email, User.id != user_id)
        ).first()
        if existing_email:
            users = session.exec(select(User)).all()
            return templates.TemplateResponse(
                "admin/users.html", 
                {
                    "request": request, 
                    "users": users, 
                    "current_user": current_user, 
                    "error": "Email již existuje"
                }
            )
        db_user.email = email
    
    if full_name:
        db_user.full_name = full_name
    
    if role:
        try:
            db_user.role = UserRole(role)
        except ValueError:
            users = session.exec(select(User)).all()
            return templates.TemplateResponse(
                "admin/users.html", 
                {
                    "request": request, 
                    "users": users, 
                    "current_user": current_user, 
                    "error": "Neplatná role uživatele"
                }
            )
    
    if password:
        from app.security.auth import get_password_hash
        db_user.hashed_password = get_password_hash(password)
    
    if is_active is not None:
        db_user.is_active = is_active
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return RedirectResponse(
        url="/admin/users",
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.post("/users/{user_id}/delete")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """Smaže uživatele z databáze"""
    # Získání uživatele z databáze
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Uživatel nenalezen")
    
    # Zabránít smazání sebe sama
    if db_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nemůžete smazat svůj vlastní účet"
        )
    
    # Smazání uživatele
    session.delete(db_user)
    session.commit()
    
    # Přesměrování zpět na seznam uživatelů
    return RedirectResponse(
        url="/admin/users",
        status_code=status.HTTP_303_SEE_OTHER
    )
