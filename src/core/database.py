import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configuración de SQLite
# En Codespaces esto creará el archivo 'finance.db' en la raíz
DB_URL = os.getenv("DB_URL", "sqlite:///finance.db")

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- MODELO: TRANSACCIONES ---
class TransactionModel(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False)        # YYYY-MM-DD
    amount = Column(Float, nullable=False)       # Guardamos float por ahora (10.50)
    currency = Column(String, default="PEN")
    category = Column(String, nullable=False)    # Inferencia de Moon
    merchant = Column(String, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

# Función para crear las tablas si no existen
def init_db():
    Base.metadata.create_all(bind=engine)