# api-gateway/app/schemas/amortization.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

class AmortizationStatus(str, Enum):
    """Estados de amortización"""
    ACTIVE = "active"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"

class AmortizationMethod(str, Enum):
    """Métodos de amortización"""
    LINEAR = "linear"
    FRENCH = "french"
    GERMAN = "german"
    DECREASING = "decreasing"

class PaymentFrequency(str, Enum):
    """Frecuencias de pago"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    BIANNUAL = "biannual"
    ANNUAL = "annual"

class AmortizationBase(BaseModel):
    """Schema base para amortización"""
    reference: str = Field(..., min_length=1, max_length=100, description="Referencia única")
    description: Optional[str] = Field(None, max_length=1000, description="Descripción")
    
    # Montos
    total_amount: Decimal = Field(..., gt=0, description="Monto total")
    
    # Configuración de cuotas
    total_installments: int = Field(..., ge=1, le=999, description="Número total de cuotas")
    interest_rate: Optional[Decimal] = Field(default=0, ge=0, le=100, description="Tasa de interés anual")
    
    # Fechas
    start_date: date = Field(..., description="Fecha de inicio")
    
    # Configuración
    amortization_method: AmortizationMethod = Field(default=AmortizationMethod.FRENCH, description="Método de amortización")
    frequency: PaymentFrequency = Field(default=PaymentFrequency.MONTHLY, description="Frecuencia de pago")
    
    # Integración SAP
    sap_doc_entry: Optional[int] = Field(None, description="DocEntry del documento SAP")
    sap_doc_type: Optional[str] = Field(None, max_length=10, description="Tipo de documento SAP")
    sap_base_ref: Optional[str] = Field(None, max_length=50, description="Referencia base SAP")
    
    # Configuraciones adicionales
    auto_payment: bool = Field(default=False, description="Crear pagos automáticamente")
    send_notifications: bool = Field(default=True, description="Enviar notificaciones")

    @validator('total_amount')
    def validate_total_amount(cls, v):
        if v <= 0:
            raise ValueError('Total amount must be greater than zero')
        return v

    @validator('interest_rate')
    def validate_interest_rate(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Interest rate must be between 0 and 100')
        return v

    @validator('start_date')
    def validate_start_date(cls, v):
        if v < date.today():
            raise ValueError('Start date cannot be in the past')
        return v

class AmortizationCreate(AmortizationBase):
    """Schema para crear amortización"""
    company_id: str = Field(..., description="ID de la compañía")
    entity_id: str = Field(..., description="ID de la entidad (cliente/proveedor)")

class AmortizationUpdate(BaseModel):
    """Schema para actualizar amortización"""
    reference: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    interest_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    status: Optional[AmortizationStatus] = None
    auto_payment: Optional[bool] = None
    send_notifications: Optional[bool] = None
    
    @validator('interest_rate')
    def validate_interest_rate(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Interest rate must be between 0 and 100')
        return v

class AmortizationResponse(AmortizationBase):
    """Schema de respuesta para amortización"""
    id: str
    company_id: str
    entity_id: str
    
    # Campos calculados
    pending_amount: Decimal
    paid_amount: Decimal
    paid_installments: int
    installment_amount: Decimal
    total_interest: Decimal
    end_date: Optional[date]
    next_due_date: Optional[date]
    status: AmortizationStatus
    
    # Información de la entidad
    entity_name: Optional[str] = None
    entity_type: Optional[str] = None
    entity_card_code: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True

class AmortizationListItem(BaseModel):
    """Schema para item en lista de amortizaciones"""
    id: str
    reference: str
    entity_name: str
    entity_type: str
    total_amount: Decimal
    pending_amount: Decimal
    paid_installments: int
    total_installments: int
    next_due_date: Optional[date]
    status: AmortizationStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

class AmortizationListResponse(BaseModel):
    """Schema para lista paginada de amortizaciones"""
    items: List[AmortizationListItem]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool

class AmortizationDetailResponse(AmortizationResponse):
    """Schema detallado de amortización con cuotas"""
    installments: Optional[List['InstallmentResponse']] = None

class AmortizationSummary(BaseModel):
    """Schema para resumen de amortizaciones"""
    total_amortizations: int
    total_amount: Decimal
    paid_amount: Decimal
    pending_amount: Decimal
    overdue_amount: Decimal
    overdue_count: int
    active_count: int
    completed_count: int
    
    # Tendencias (comparado con período anterior)
    amortizations_trend: float = 0
    amount_trend: float = 0
    payments_trend: float = 0

class AmortizationCalculation(BaseModel):
    """Schema para cálculo de amortización"""
    total_amount: Decimal = Field(..., gt=0)
    total_installments: int = Field(..., ge=1, le=999)
    interest_rate: Decimal = Field(default=0, ge=0, le=100)
    amortization_method: AmortizationMethod = Field(default=AmortizationMethod.FRENCH)
    frequency: PaymentFrequency = Field(default=PaymentFrequency.MONTHLY)
    start_date: date

class CalculatedInstallment(BaseModel):
    """Schema para cuota calculada"""
    number: int
    due_date: date
    principal: Decimal
    interest: Decimal
    total: Decimal
    balance: Decimal

class AmortizationCalculationResponse(BaseModel):
    """Schema de respuesta para cálculo de amortización"""
    installments: List[CalculatedInstallment]
    total_principal: Decimal
    total_interest: Decimal
    total_amount: Decimal
    effective_rate: Decimal
