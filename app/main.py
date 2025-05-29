import os
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Import pro vytvoření databáze
from app.database.db import create_db_and_tables, get_session

# Import routů
from app.routes import auth, users, admin

# Import pro databázi
from sqlmodel import Session

# Vytvoření instance aplikace
app = FastAPI(title="FastAPI Web Admin Panel")

# Připojení routů k aplikaci
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)

# Nastavení statických souborů
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Nastavení šablon
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
templates = Jinja2Templates(directory=templates_dir)

# Funkce pro vytvoření databáze při startu aplikace
@app.on_event("startup")
def on_startup():
    """Vytvoří databázi a tabulky při startu aplikace"""
    create_db_and_tables()

# Získání aktuálního uživatele z cookie
async def get_current_user_from_cookie(request: Request, session: Session = Depends(get_session)):
    """Získá aktuálního uživatele z cookie"""
    try:
        # Získání přístupového tokenu z cookie
        token = request.cookies.get("access_token")
        if not token or not token.startswith("Bearer "):
            return None
        
        # Odstranění prefixu "Bearer "
        token = token.replace("Bearer ", "")
        
        # Získání uživatele pomocí funkce z OAuth2
        from app.security.oauth2 import get_current_user
        user = await get_current_user(token=token, session=session)
        return user
    except HTTPException:
        return None

# Hlavní stránka
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, session: Session = Depends(get_session)):
    """Hlavní stránka aplikace"""
    # Získání aktuálního uživatele (pokud je přihlášen)
    user = await get_current_user_from_cookie(request, session)
    
    return templates.TemplateResponse(
        "frontend/index.html", 
        {"request": request, "user": user}
    )

# Dashboard stránka (vyžaduje přihlášení)
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, session: Session = Depends(get_session)):
    """Dashboard stránka, přístupná pouze pro přihlášené uživatele"""
    # Získání aktuálního uživatele
    user = await get_current_user_from_cookie(request, session)
    
    # Pokud není uživatel přihlášen, přesměrujeme na přihlášení
    if not user:
        return RedirectResponse(
            url="/auth/login",
            status_code=status.HTTP_303_SEE_OTHER
        )
    
    # V závislosti na roli uživatele zobrazíme jiný dashboard
    if user.role == "admin":
        return templates.TemplateResponse(
            "admin/dashboard.html", 
            {"request": request, "user": user}
        )
    else:
        return templates.TemplateResponse(
            "frontend/dashboard.html", 
            {"request": request, "user": user}
        )

# Stránka s kontaktem
@app.get("/kontakt", response_class=HTMLResponse)
async def kontakt(request: Request, session: Session = Depends(get_session)):
    """Kontaktní stránka"""
    # Získání aktuálního uživatele (pokud je přihlášen)
    user = await get_current_user_from_cookie(request, session)
    
    return templates.TemplateResponse(
        "frontend/kontakt.html", 
        {"request": request, "user": user}
    )

# Hlavní vstupní bod pro spuštění aplikace
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
