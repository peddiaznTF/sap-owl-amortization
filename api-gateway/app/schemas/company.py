# # api-gateway/app/schemas/company.py
# from pydantic import BaseModel, Field, validator
# from typing import Optional, Dict, Any
# from datetime import datetime
# from decimal import Decimal

# class CompanyBase(BaseModel):
#     """Schema base para compañía"""
#     name: str = Field(..., min_length=1, max_length=255, description="Nombre de la compañía")
#     currency: str = Field(default="EUR", min_length=3, max_length=3, description="Moneda de la compañía")
#     sap_database: str = Field(..., min_length=1, max_length=50, description="Base de datos SAP")
#     description: Optional[str] = Field(None, max_length=500, description="Descripción de la compañía")
    
#     # Configuraciones por defecto
#     default_amortization_account: Optional[str] = Field(None, max_length=20, description="Cuenta de amortización por defecto")
#     default_interest_rate: Optional[Decimal] = Field(default=0.0, ge=0, le=100, description="Tasa de interés por defecto")
#     default_installments: Optional[int] = Field(default=12, ge=1, le=999, description="Número de cuotas por defecto")
    
#     # Configuraciones SAP
#     sap_server_url: Optional[str] = Field(None, max_length=255, description="URL del servidor SAP")
#     sap_username: Optional[str] = Field(None, max_length=100, description="Usuario SAP")
#     sap_company_db: Optional[str] = Field(None, max_length=50, description="Base de datos de compañía SAP")

#     @validator('currency')
#     def validate_currency(cls, v):
#         if v and len(v) != 3:
#             raise ValueError('Currency must be a 3-letter code')
#         return v.upper() if v else v

#     @validator('default_interest_rate')
#     def validate_interest_rate(cls, v):
#         if v is not None and (v < 0 or v > 100):
#             raise ValueError('Interest rate must be between 0 and 100')
#         return v

# class CompanyCreate(CompanyBase):
#     """Schema para crear compañía"""
#     id: str = Field(..., min_length=1, max_length=50, description="ID único de la compañía")
    
#     @validator('id')
#     def validate_id(cls, v):
#         if not v.replace('_', '').replace('-', '').isalnum():
#             raise ValueError('Company ID must contain only alphanumeric characters, hyphens, and underscores')
#         return v.upper()

# class CompanyUpdate(CompanyBase):
#     """Schema para actualizar compañía"""
#     name: Optional[str] = Field(None, min_length=1, max_length=255)
#     currency: Optional[str] = Field(None, min_length=3, max_length=3)
#     sap_database: Optional[str] = Field(None, min_length=1, max_length=50)

# class CompanyResponse(CompanyBase):
#     """Schema de respuesta para compañía"""
#     id: str
#     created_at: datetime
#     updated_at: Optional[datetime]
#     is_active: bool
    
#     # Estadísticas calculadas
#     total_amortizations: Optional[int] = 0
#     total_amount: Optional[Decimal] = 0
#     active_amortizations: Optional[int] = 0
    
#     class Config:
#         from_attributes = True

# class CompanyListResponse(BaseModel):
#     """Schema para lista de compañías"""
#     companies: list[CompanyResponse]
#     total: int
#     page: int
#     page_size: int

# class CompanySettingCreate(BaseModel):
#     """Schema para crear configuración de compañía"""
#     setting_key: str = Field(..., min_length=1, max_length=100)
#     setting_value: str = Field(..., max_length=1000)
#     setting_type: str = Field(default="string", regex="^(string|number|boolean|json)$")
#     description: Optional[str] = Field(None, max_length=255)

# class CompanySettingResponse(CompanySettingCreate):
#     """Schema de respuesta para configuración de compañía"""
#     id: str
#     company_id: str
#     created_at: datetime
#     updated_at: Optional[datetime]
#     is_active: bool
    
#     class Config:
#         from_attributes = True

# api-gateway/app/schemas/company.py
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

class CompanyBase(BaseModel):
    """Schema base para compañía"""
    name: str = Field(..., min_length=1, max_length=255, description="Nombre de la compañía")
    currency: str = Field(default="EUR", min_length=3, max_length=3, description="Moneda de la compañía")
    sap_database: str = Field(..., min_length=1, max_length=50, description="Base de datos SAP")
    description: Optional[str] = Field(None, max_length=500, description="Descripción de la compañía")
    
    # Configuraciones por defecto
    default_amortization_account: Optional[str] = Field(None, max_length=20, description="Cuenta de amortización por defecto")
    default_interest_rate: Optional[Decimal] = Field(default=0.0, ge=0, le=100, description="Tasa de interés por defecto")
    default_installments: Optional[int] = Field(default=12, ge=1, le=999, description="Número de cuotas por defecto")
    
    # Configuraciones SAP
    sap_server_url: Optional[str] = Field(None, max_length=255, description="URL del servidor SAP")
    sap_username: Optional[str] = Field(None, max_length=100, description="Usuario SAP")
    sap_company_db: Optional[str] = Field(None, max_length=50, description="Base de datos de compañía SAP")

    @validator('currency')
    def validate_currency(cls, v):
        if v and len(v) != 3:
            raise ValueError('Currency must be a 3-letter code')
        return v.upper() if v else v

    @validator('default_interest_rate')
    def validate_interest_rate(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Interest rate must be between 0 and 100')
        return v

class CompanyCreate(CompanyBase):
    """Schema para crear compañía"""
    id: str = Field(..., min_length=1, max_length=50, description="ID único de la compañía")
    
    @validator('id')
    def validate_id(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Company ID must contain only alphanumeric characters, hyphens, and underscores')
        return v.upper()

class CompanyUpdate(CompanyBase):
    """Schema para actualizar compañía"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    sap_database: Optional[str] = Field(None, min_length=1, max_length=50)

class CompanyResponse(CompanyBase):
    """Schema de respuesta para compañía"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool
    
    # Estadísticas calculadas
    total_amortizations: Optional[int] = 0
    total_amount: Optional[Decimal] = 0
    active_amortizations: Optional[int] = 0
    
    class Config:
        from_attributes = True

class CompanyListResponse(BaseModel):
    """Schema para lista de compañías"""
    companies: list[CompanyResponse]
    total: int
    page: int
    page_size: int

class CompanySettingCreate(BaseModel):
    """Schema para crear configuración de compañía"""
    setting_key: str = Field(..., min_length=1, max_length=100)
    setting_value: str = Field(..., max_length=1000)
    setting_type: str = Field(default="string", pattern="^(string|number|boolean|json)$")
    description: Optional[str] = Field(None, max_length=255)

class CompanySettingResponse(CompanySettingCreate):
    """Schema de respuesta para configuración de compañía"""
    id: str
    company_id: str
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True