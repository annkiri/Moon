import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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
    date = Column(String, nullable=False)  # YYYY-MM-DD
    amount = Column(Float, nullable=False)  # Guardamos float por ahora (10.50)
    currency = Column(String, default="PEN")
    category = Column(String, nullable=False)  # Inferencia de Moon
    merchant = Column(String, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


# --- TABLA DE NOTAS ---
class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    tags = Column(
        String, nullable=True
    )  # Guardaremos las tags como string separado por comas "tag1,tag2"
    category = Column(String, default="general")
    created_at = Column(DateTime, default=datetime.now)


# --- TABLA DE TAREAS ---
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    due_date = Column(
        DateTime, nullable=True
    )  # Aquí guardamos la fecha del recordatorio
    priority = Column(String, default="normal")
    status = Column(String, default="pending")  # pending, done, archived
    created_at = Column(DateTime, default=datetime.now)


# ---src/core/database.py ---
# (Mantén tus imports existentes y agrega UserProfile)


class UserProfile(Base):
    """
    Tabla para almacenar 'Hechos Singulares' del usuario.
    Ej: Nombre, Edad, Ciudad, Equipo de Fútbol.
    NO para listas o notas largas.
    """

    __tablename__ = "user_profile"

    id = Column(Integer, primary_key=True, index=True)
    # La clave debe ser única (ej: 'user_name'). Si existe, se sobrescribe.
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(String, nullable=False)
    category = Column(
        String, default="general"
    )  # ej: 'personal', 'preferences', 'health'
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# Función para crear las tablas si no existen
def init_db():
    Base.metadata.create_all(bind=engine)
