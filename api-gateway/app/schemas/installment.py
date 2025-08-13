# api-gateway/app/schemas/installment.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

class InstallmentStatus(str, Enum):
    """Estados de cuota"""
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    PARTIAL = "partial"

class InstallmentBase(BaseModel):
    """Schema base para cuota"""
    installment_number: int = Field(..., ge=1, description="Número de cuota")
    due_date: date = Field(..., description="Fecha de vencimiento")
    principal_amount: Decimal = Field(..., ge=0, description="Monto de capital")
    interest_amount: Decimal = Field(default=0, ge=0, description="Monto de interés")
    total_amount: Decimal = Field(..., gt=0, description="Monto total de la cuota")
    remaining_balance: Optional[Decimal] = Field(None, ge=0, description="Saldo restante")
    notes: Optional[str] = Field(None, max_length=1000, description="Notas")

    @validator('total_amount')
    def validate_total_amount(cls, v, values):
        principal = values.get('principal_amount', 0)
        interest = values.get('interest_amount', 0)
        if v != principal + interest:
            raise ValueError('Total amount must equal principal + interest')
        return v

class InstallmentCreate(InstallmentBase):
    """Schema para crear cuota"""
    amortization_id: str = Field(..., description="ID de la amortización")

class InstallmentUpdate(BaseModel):
    """Schema para actualizar cuota"""
    due_date: Optional[date] = None
    principal_amount: Optional[Decimal] = Field(None, ge=0)
    interest_amount: Optional[Decimal] = Field(None, ge=0)
    total_amount: Optional[Decimal] = Field(None, gt=0)
    notes: Optional[str] = Field(None, max_length=1000)
    late_fee: Optional[Decimal] = Field(None, ge=0)

class InstallmentResponse(InstallmentBase):
    """Schema de respuesta para cuota"""
    id: str
    amortization_id: str
    paid_amount: Decimal
    payment_date: Optional[date]
    status: InstallmentStatus
    late_fee: Decimal
    
    # Integración SAP
    sap_payment_entry: Optional[int]
    sap_journal_entry: Optional[int]
    
    # Campos calculados
    is_overdue: bool
    days_overdue: int
    remaining_amount: Decimal
    payment_percentage: float
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True

class PaymentCreate(BaseModel):
    """Schema para crear pago"""
    amount: Decimal = Field(..., gt=0, description="Monto del pago")
    payment_date: date = Field(default_factory=date.today, description="Fecha del pago")
    notes: Optional[str] = Field(None, max_length=500, description="Notas del pago")
    create_sap_entry: bool = Field(default=True, description="Crear asiento en SAP")
    
    # Información de pago
    payment_method: Optional[str] = Field(None, max_length=50, description="Método de pago")
    bank_account: Optional[str] = Field(None, max_length=50, description="Cuenta bancaria")
    reference_number: Optional[str] = Field(None, max_length=50, description="Número de referencia")

    @validator('payment_date')
    def validate_payment_date(cls, v):
        if v > date.today():
            raise ValueError('Payment date cannot be in the future')
        return v

class PaymentResponse(BaseModel):
    """Schema de respuesta para pago"""
    id: str
    installment_id: str
    amount: Decimal
    payment_date: date
    notes: Optional[str]
    payment_method: Optional[str]
    bank_account: Optional[str]
    reference_number: Optional[str]
    
    # Integración SAP
    sap_payment_entry: Optional[int]
    sap_journal_entry: Optional[int]
    
    # Estado
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class MultiplePaymentCreate(BaseModel):
    """Schema para pago múltiple"""
    installment_ids: List[str] = Field(..., min_items=1, description="IDs de las cuotas")
    payment_date: date = Field(default_factory=date.today, description="Fecha del pago")
    notes: Optional[str] = Field(None, max_length=500, description="Notas del pago")
    create_sap_entries: bool = Field(default=True, description="Crear asientos en SAP")
    payment_method: Optional[str] = Field(None, max_length=50, description="Método de pago")

class InstallmentSummary(BaseModel):
    """Schema para resumen de cuotas"""
    total_installments: int
    paid_installments: int
    pending_installments: int
    overdue_installments: int
    
    total_amount: Decimal
    paid_amount: Decimal
    pending_amount: Decimal
    overdue_amount: Decimal
    
    next_due_date: Optional[date]
    last_payment_date: Optional[date]