# FastAPI Web Admin Panel

Komplexní webová aplikace s administračním rozhraním, registrací a přihlášením uživatelů, postavená na FastAPI a SQLModel.

![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?style=flat-square&logo=fastapi)
![SQLModel](https://img.shields.io/badge/SQLModel-0.0.8-4479A1?style=flat-square&logo=sqlite)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat-square&logo=bootstrap)
![HTMX](https://img.shields.io/badge/HTMX-1.9.5-3E54AC?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square&logo=docker)

## Funkce

- 🔑 **Autentizace uživatelů** - OAuth2 s JWT tokeny pro bezpečné přihlášení
- 👤 **Správa uživatelů** - Registrace, přihlášení a úprava profilu
- 💻 **Admin panel** - Kompletní správa uživatelů (CRUD operace)
- 📦 **HTMX Integrace** - Dynamické uživatelské rozhraní bez nutnosti JavaScriptu
- 🌐 **Responzivní design** - Bootstrap 5 pro moderní vzhled na všech zařízeních
- 💾 **SQLite s SQLModel** - Jednoduchá a efektivní práce s databází
- 🚀 **Alembic migrace** - Správa databázového schématu
- 📡 **API dokumentace** - Automaticky generovaná Swagger dokumentace
- 💻 **Dockerizace** - Připravené Docker a Docker Compose konfigurace

## Technologický stack

### Backend
- **FastAPI** - Rychlý Python web framework
- **SQLModel** - ORM pro práci s SQL databázemi
- **SQLite** - Databáze
- **Alembic** - Databázové migrace
- **Pydantic** - Validace dat
- **JWT** - JSON Web Token pro autentizaci
- **Passlib** - Hašování hesel

### Frontend
- **Jinja2** - Šablony pro generování HTML
- **Bootstrap 5** - CSS framework
- **HTMX** - Dynamické uživatelské rozhraní bez JS
- **Font Awesome** - Ikony

### DevOps
- **Docker** - Kontejnerizace aplikace
- **Docker Compose** - Orchestrace kontejnerů
- **Uvicorn** - ASGI server

## Instalace

### Prostřednictvím Pythonu

1. Naklonujte repozitář:
   ```bash
   git clone https://github.com/uzivatelske-jmeno/FastAPI-Web-Admin-Panel.git
   cd FastAPI-Web-Admin-Panel
   ```

2. Vytvořte virtuální prostředí a nainstalujte závislosti:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Na Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Spusťte migrace databáze:
   ```bash
   alembic upgrade head
   ```

4. Spusťte aplikaci (pozor na port ho mám nastaven na 8000):
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8004
   ```

### Prostřednictvím Dockeru

1. Naklonujte repozitář:
   ```bash
   git clone https://github.com/uzivatelske-jmeno/FastAPI-Web-Admin-Panel.git
   cd FastAPI-Web-Admin-Panel
   ```

2. Spusťte pomocí Docker Compose (vývojové prostředí):
   ```bash
   docker-compose up
   ```

   Nebo pro produkční prostředí:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## Použití

 Po spuštění bude aplikace dostupná na:

- Web aplikace: http://localhost:8004
- API dokumentace: http://localhost:8004/docs
- Alternativní API dokumentace: http://localhost:8004/redoc

### Výchozí admin přihlašovací údaje

```
Uživatelské jméno: admin
Heslo: admin123
```

> **Poznámka**: Po prvním přihlášení si změňte heslo!

## Struktura projektu

```
app/
├── database/            # Databázové soubory a nastavení
├── migrations/          # Alembic migrace
├── models/              # SQLModel modely (User)
├── routes/              # FastAPI routy
├── security/            # Autentizace a autorizace
├── static/              # Statické soubory (CSS, JS)
├── templates/           # Jinja2 šablony
│   ├── admin/          # Administrátorské šablony
│   └── frontend/       # Šablony pro běžné uživatele
└── utils/               # Pomocné funkce
```

## API Endpointy

Aplikace poskytuje následující API endpointy:

- **Autentizace**
  - `POST /auth/token` - Získání JWT tokenu
  - `GET /auth/login` - Přihlašovací formulář
  - `POST /auth/login` - Zpracování přihlášení
  - `GET /auth/register` - Registrační formulář
  - `POST /auth/register` - Zpracování registrace
  - `GET /auth/logout` - Odhlášení

- **Uživatelé**
  - `GET /users/profile` - Zobrazení profilu
  - `POST /users/profile` - Úprava profilu
  - `GET /users/dashboard` - Uživatelský dashboard

- **Admin**
  - `GET /admin/users` - Seznam uživatelů
  - `POST /admin/users/create` - Vytvoření uživatele
  - `POST /admin/users/{user_id}/edit` - Úprava uživatele
  - `POST /admin/users/{user_id}/delete` - Smazání uživatele

- **Obecné**
  - `GET /` - Úvodní stránka
  - `GET /dashboard` - Přesměrování na správný dashboard
  - `GET /kontakt` - Kontaktní stránka

## Databázové migrace

Pro správu databáze používáme Alembic:

```bash
# Inicializace databáze a spuštění migrací
alembic upgrade head

# Vytvoření nové migrace
alembic revision --autogenerate -m "popis změn"
```

## Přispívání

1. Forkněte repozitář
2. Vytvořte feature branch (`git checkout -b feature/moje-nova-funkce`)
3. Commitněte vaše změny (`git commit -am 'Přidána nová funkce'`)
4. Pushněte do branche (`git push origin feature/moje-nova-funkce`)
5. Vytvořte nový Pull Request

## Licence

Tento projekt je licencován pod MIT licencí - viz soubor [LICENSE](LICENSE) pro detaily.

## Kontakt

Pro jakékoliv dotazy nebo připomínky můžete vytvořit issue v tomto repozitáři nebo nás kontaktovat přímo.
