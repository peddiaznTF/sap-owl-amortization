# api-gateway/app/utils/validators.py
import re
from typing import Optional, Any
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

def validate_email(email: str) -> bool:
    """Validar formato de email"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_currency(currency: str) -> bool:
    """Validar código de moneda (ISO 4217)"""
    if not currency or len(currency) != 3:
        return False
    
    # Lista de códigos de moneda comunes
    valid_currencies = {
        'EUR', 'USD', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD',
        'SEK', 'NOK', 'DKK', 'PLN', 'CZK', 'HUF', 'RON', 'BGN',
        'HRK', 'RUB', 'TRY', 'BRL', 'MXN', 'ARS', 'CLP', 'COP',
        'PEN', 'UYU', 'CNY', 'INR', 'KRW', 'SGD', 'THB', 'MYR',
        'IDR', 'PHP', 'VND', 'ZAR', 'EGP', 'NGN', 'KES'
    }
    
    return currency.upper() in valid_currencies

def validate_date_range(date_from: Optional[date], date_to: Optional[date]) -> bool:
    """Validar que el rango de fechas sea válido"""
    if not date_from or not date_to:
        return True  # Opcional
    
    return date_from <= date_to

def validate_amount(amount: Any, min_value: float = 0, max_value: Optional[float] = None) -> bool:
    """Validar monto monetario"""
    try:
        if isinstance(amount, str):
            amount = Decimal(amount)
        elif isinstance(amount, (int, float)):
            amount = Decimal(str(amount))
        elif not isinstance(amount, Decimal):
            return False
        
        if amount < min_value:
            return False
        
        if max_value is not None and amount > max_value:
            return False
        
        # Verificar que no tenga más de 2 decimales
        if amount.as_tuple().exponent < -2:
            return False
        
        return True
        
    except (InvalidOperation, ValueError):
        return False

def validate_percentage(percentage: Any, min_value: float = 0, max_value: float = 100) -> bool:
    """Validar porcentaje"""
    try:
        if isinstance(percentage, str):
            percentage = float(percentage)
        elif not isinstance(percentage, (int, float, Decimal)):
            return False
        
        return min_value <= float(percentage) <= max_value
        
    except (ValueError, TypeError):
        return False

def validate_installments(installments: Any, min_value: int = 1, max_value: int = 999) -> bool:
    """Validar número de cuotas"""
    try:
        if isinstance(installments, str):
            installments = int(installments)
        elif not isinstance(installments, int):
            return False
        
        return min_value <= installments <= max_value
        
    except (ValueError, TypeError):
        return False

def validate_sap_company_id(company_id: str) -> bool:
    """Validar ID de compañía SAP"""
    if not company_id:
        return False
    
    # Debe ser alfanumérico, guiones y guiones bajos permitidos
    pattern = r'^[A-Z0-9_-]+$'
    if not re.match(pattern, company_id):
        return False
    
    # Longitud entre 3 y 50 caracteres
    return 3 <= len(company_id) <= 50

def validate_sap_card_code(card_code: str) -> bool:
    """Validar código de socio de negocio SAP"""
    if not card_code:
        return False
    
    # Debe ser alfanumérico, longitud máxima 15
    pattern = r'^[A-Z0-9]+$'
    if not re.match(pattern, card_code):
        return False
    
    return 1 <= len(card_code) <= 15

def validate_reference(reference: str) -> bool:
    """Validar referencia de amortización"""
    if not reference:
        return False
    
    # Debe contener al menos un carácter alfanumérico
    if not re.search(r'[A-Za-z0-9]', reference):
        return False
    
    # Longitud entre 1 y 100 caracteres
    return 1 <= len(reference.strip()) <= 100

def validate_amortization_method(method: str) -> bool:
    """Validar método de amortización"""
    valid_methods = ['linear', 'french', 'german', 'decreasing']
    return method in valid_methods

def validate_payment_frequency(frequency: str) -> bool:
    """Validar frecuencia de pago"""
    valid_frequencies = ['monthly', 'quarterly', 'biannual', 'annual']
    return frequency in valid_frequencies

def validate_status(status: str, entity_type: str = 'amortization') -> bool:
    """Validar estado según tipo de entidad"""
    status_map = {
        'amortization': ['active', 'completed', 'overdue', 'suspended', 'cancelled'],
        'installment': ['pending', 'paid', 'overdue', 'partial'],
        'user': ['active', 'inactive', 'pending', 'suspended']
    }
    
    valid_statuses = status_map.get(entity_type, [])
    return status in valid_statuses

def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """Limpiar y sanitizar string"""
    if not value:
        return ""
    
    # Remover caracteres de control y espacios extra
    cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    if max_length:
        cleaned = cleaned[:max_length]
    
    return cleaned

def validate_phone_number(phone: str) -> bool:
    """Validar número de teléfono"""
    if not phone:
        return True  # Opcional
    
    # Patrón básico para números internacionales
    pattern = r'^\+?[1-9]\d{1,14}$'
    
    # Remover espacios, guiones y paréntesis
    cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    return bool(re.match(pattern, cleaned_phone))

def validate_url(url: str) -> bool:
    """Validar URL"""
    if not url:
        return True  # Opcional
    
    pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    return bool(re.match(pattern, url))

class ValidationError(Exception):
    """Excepción personalizada para errores de validación"""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)

def validate_required_fields(data: dict, required_fields: list) -> None:
    """Validar que los campos requeridos estén presentes"""
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}"
        )