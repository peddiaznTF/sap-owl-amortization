# api-gateway/app/models/entity.py
from sqlalchemy import Column, String, ForeignKey, UniqueConstraint, Integer
from sqlalchemy.orm import relationship
from . import BaseModel

class Entity(BaseModel):
    """Modelo para clientes y proveedores"""
    __tablename__ = "entities"
    
    company_id = Column(String(50), ForeignKey('companies.id'), nullable=False)
    sap_card_code = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(20), nullable=False)  # 'cliente' o 'proveedor'
    currency = Column(String(3), default='EUR')
    
    # Información adicional de SAP
    sap_card_name = Column(String(255))
    sap_group_code = Column(String(20))
    credit_limit = Column(Numeric(18, 2))
    current_balance = Column(Numeric(18, 2))
    
    # Configuración de amortización
    amortization_enabled = Column(Boolean, default=False)
    default_amortization_config = Column(String(50))
    
    # Relaciones
    company = relationship("Company", back_populates="entities")
    amortizations = relationship("Amortization", back_populates="entity", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('company_id', 'sap_card_code', name='unique_company_entity'),
    )
    
    def __repr__(self):
        return f"<Entity(card_code='{self.sap_card_code}', name='{self.name}', type='{self.type}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'sap_card_code': self.sap_card_code,
            'name': self.name,
            'type': self.type,
            'currency': self.currency,
            'sap_card_name': self.sap_card_name,
            'sap_group_code': self.sap_group_code,
            'credit_limit': float(self.credit_limit) if self.credit_limit else 0.0,
            'current_balance': float(self.current_balance) if self.current_balance else 0.0,
            'amortization_enabled': self.amortization_enabled,
            'default_amortization_config': self.default_amortization_config,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }