# # api-gateway/app/models/company.py
# from sqlalchemy import Column, String, Text, Numeric
# from sqlalchemy.orm import relationship
# from . import BaseModel

# class Company(BaseModel):
#     """Modelo para gestión de compañías"""
#     __tablename__ = "companies"
    
#     # Usar el SAP Company ID como primary key
#     id = Column(String(50), primary_key=True)
#     name = Column(String(255), nullable=False)
#     currency = Column(String(3), nullable=False, default='EUR')
#     sap_database = Column(String(50), nullable=False)
#     description = Column(Text)
    
#     # Configuraciones específicas
#     default_amortization_account = Column(String(20))
#     default_interest_rate = Column(Numeric(5, 4), default=0.0)
#     default_installments = Column(Integer, default=12)
    
#     # Configuraciones de integración SAP
#     sap_server_url = Column(String(255))
#     sap_username = Column(String(100))
#     sap_company_db = Column(String(50))
    
#     # Relaciones
#     entities = relationship("Entity", back_populates="company", cascade="all, delete-orphan")
#     amortizations = relationship("Amortization", back_populates="company", cascade="all, delete-orphan")
#     settings = relationship("CompanySetting", back_populates="company", cascade="all, delete-orphan")
    
#     def __repr__(self):
#         return f"<Company(id='{self.id}', name='{self.name}')>"
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'name': self.name,
#             'currency': self.currency,
#             'sap_database': self.sap_database,
#             'description': self.description,
#             'default_amortization_account': self.default_amortization_account,
#             'default_interest_rate': float(self.default_interest_rate) if self.default_interest_rate else 0.0,
#             'default_installments': self.default_installments,
#             'created_at': self.created_at.isoformat() if self.created_at else None,
#             'updated_at': self.updated_at.isoformat() if self.updated_at else None,
#             'is_active': self.is_active
#         }

# class CompanySetting(BaseModel):
#     """Configuraciones específicas por compañía"""
#     __tablename__ = "company_settings"
    
#     company_id = Column(String(50), ForeignKey('companies.id'), nullable=False)
#     setting_key = Column(String(100), nullable=False)
#     setting_value = Column(Text)
#     setting_type = Column(String(20), default='string')  # string, number, boolean, json
#     description = Column(String(255))
    
#     # Relaciones
#     company = relationship("Company", back_populates="settings")
    
#     __table_args__ = (
#         UniqueConstraint('company_id', 'setting_key', name='unique_company_setting'),
#     )
    
#     def __repr__(self):
#         return f"<CompanySetting(company_id='{self.company_id}', key='{self.setting_key}')>"
# api-gateway/app/models/company.py
from sqlalchemy import Column, String, Text, Numeric, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from . import BaseModel

class Company(BaseModel):
    """Modelo para gestión de compañías"""
    __tablename__ = "companies"
    
    # Usar el SAP Company ID como primary key
    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    currency = Column(String(3), nullable=False, default='EUR')
    sap_database = Column(String(50), nullable=False)
    description = Column(Text)
    
    # Configuraciones específicas
    default_amortization_account = Column(String(20))
    default_interest_rate = Column(Numeric(5, 4), default=0.0)
    default_installments = Column(Integer, default=12)
    
    # Configuraciones de integración SAP
    sap_server_url = Column(String(255))
    sap_username = Column(String(100))
    sap_company_db = Column(String(50))
    
    # Relaciones
    entities = relationship("Entity", back_populates="company", cascade="all, delete-orphan")
    amortizations = relationship("Amortization", back_populates="company", cascade="all, delete-orphan")
    settings = relationship("CompanySetting", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Company(id='{self.id}', name='{self.name}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'currency': self.currency,
            'sap_database': self.sap_database,
            'description': self.description,
            'default_amortization_account': self.default_amortization_account,
            'default_interest_rate': float(self.default_interest_rate) if self.default_interest_rate else 0.0,
            'default_installments': self.default_installments,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }

class CompanySetting(BaseModel):
    """Configuraciones específicas por compañía"""
    __tablename__ = "company_settings"
    
    company_id = Column(String(50), ForeignKey('companies.id'), nullable=False)
    setting_key = Column(String(100), nullable=False)
    setting_value = Column(Text)
    setting_type = Column(String(20), default='string')  # string, number, boolean, json
    description = Column(String(255))
    
    # Relaciones
    company = relationship("Company", back_populates="settings")
    
    __table_args__ = (
        UniqueConstraint('company_id', 'setting_key', name='unique_company_setting'),
    )
    
    def __repr__(self):
        return f"<CompanySetting(company_id='{self.company_id}', key='{self.setting_key}')>"