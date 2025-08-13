# api-gateway/app/schemas/__init__.py
from .company import CompanyCreate, CompanyUpdate, CompanyResponse
from .entity import EntityCreate, EntityUpdate, EntityResponse
from .amortization import (
    AmortizationCreate, AmortizationUpdate, AmortizationResponse,
    AmortizationListResponse, AmortizationDetailResponse
)
from .installment import (
    InstallmentCreate, InstallmentUpdate, InstallmentResponse,
    PaymentCreate, PaymentResponse
)
from .auth import UserCreate, UserLogin, UserResponse, Token
from .common import PaginatedResponse, MessageResponse

__all__ = [
    # Company schemas
    "CompanyCreate", "CompanyUpdate", "CompanyResponse",
    
    # Entity schemas
    "EntityCreate", "EntityUpdate", "EntityResponse",
    
    # Amortization schemas
    "AmortizationCreate", "AmortizationUpdate", "AmortizationResponse",
    "AmortizationListResponse", "AmortizationDetailResponse",
    
    # Installment schemas
    "InstallmentCreate", "InstallmentUpdate", "InstallmentResponse",
    "PaymentCreate", "PaymentResponse",
    
    # Auth schemas
    "UserCreate", "UserLogin", "UserResponse", "Token",
    
    # Common schemas
    "PaginatedResponse", "MessageResponse"
]
