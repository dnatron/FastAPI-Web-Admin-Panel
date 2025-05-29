# Databázové spojení pomocí SQLModel a SQLite
from sqlmodel import create_engine, Session, SQLModel
import os
from typing import Generator

# Získáme absolutní cestu k projektu
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Vytvoření SQLite databáze ve složce database
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'database', 'app.db')}"

# Vytvoření enginu pro komunikaci s databází
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

# Funkce pro vytvoření a správu databázových relací
def create_db_and_tables():
    """Vytvoří všechny tabulky v databázi, které jsou definované pomocí SQLModel"""
    SQLModel.metadata.create_all(engine)

# Funkce pro poskytnutí databázové session jako generátor
def get_session() -> Generator[Session, None, None]:
    """Poskytuje databázovou session pro operace s databází"""
    with Session(engine) as session:
        yield session
