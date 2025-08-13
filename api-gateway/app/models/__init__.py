# api-gateway/app/models/__init__.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class BaseModel(Base):
    """Modelo base con campos comunes"""
    __abstract__ = True
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

# Importar todos los modelos
from .company import Company
from .entity import Entity
from .amortization import Amortization, AmortizationInstallment
from .user import User

__all__ = [
    "Base",
    "BaseModel", 
    "Company",
    "Entity",
    "Amortization",
    "AmortizationInstallment",
    "User"
]