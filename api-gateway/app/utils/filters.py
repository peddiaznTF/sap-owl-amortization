# api-gateway/app/utils/filters.py
from typing import Optional, List, Any, Dict
from datetime import date, datetime
from pydantic import BaseModel, validator
from sqlalchemy.orm import Query
from sqlalchemy import and_, or_, func, text

class BaseFilters(BaseModel):
    """Filtros base para todas las entidades"""
    company_id: Optional[str] = None
    is_active: Optional[bool] = True
    created_from: Optional[date] = None
    created_to: Optional[date] = None
    updated_from: Optional[date] = None
    updated_to: Optional[date] = None
    search: Optional[str] = None

class AmortizationFilters(BaseFilters):
    """Filtros específicos para amortizaciones"""
    entity_type: Optional[str] = None  # 'cliente' o 'proveedor'
    entity_id: Optional[str] = None
    entity_name: Optional[str] = None
    status: Optional[str] = None
    amortization_method: Optional[str] = None
    frequency: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    amount_from: Optional[float] = None
    amount_to: Optional[float] = None
    installments_from: Optional[int] = None
    installments_to: Optional[int] = None
    overdue_only: Optional[bool] = False
    completed_only: Optional[bool] = False
    pending_only: Optional[bool] = False
    
    @validator('entity_type')
    def validate_entity_type(cls, v):
        if v and v not in ['cliente', 'proveedor']:
            raise ValueError('entity_type must be "cliente" or "proveedor"')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['active', 'completed', 'overdue', 'suspended', 'cancelled']
        if v and v not in valid_statuses:
            raise ValueError(f'status must be one of: {valid_statuses}')
        return v
    
    @validator('amortization_method')
    def validate_method(cls, v):
        valid_methods = ['linear', 'french', 'german', 'decreasing']
        if v and v not in valid_methods:
            raise ValueError(f'amortization_method must be one of: {valid_methods}')
        return v
    
    @validator('frequency')
    def validate_frequency(cls, v):
        valid_frequencies = ['monthly', 'quarterly', 'biannual', 'annual']
        if v and v not in valid_frequencies:
            raise ValueError(f'frequency must be one of: {valid_frequencies}')
        return v

class InstallmentFilters(BaseFilters):
    """Filtros para cuotas de amortización"""
    amortization_id: Optional[str] = None
    status: Optional[str] = None
    due_date_from: Optional[date] = None
    due_date_to: Optional[date] = None
    payment_date_from: Optional[date] = None
    payment_date_to: Optional[date] = None
    amount_from: Optional[float] = None
    amount_to: Optional[float] = None
    overdue_only: Optional[bool] = False
    paid_only: Optional[bool] = False
    pending_only: Optional[bool] = False
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['pending', 'paid', 'overdue', 'partial']
        if v and v not in valid_statuses:
            raise ValueError(f'status must be one of: {valid_statuses}')
        return v

class EntityFilters(BaseFilters):
    """Filtros para entidades (clientes/proveedores)"""
    entity_type: Optional[str] = None
    sap_card_code: Optional[str] = None
    name: Optional[str] = None
    currency: Optional[str] = None
    amortization_enabled: Optional[bool] = None

def apply_amortization_filters(query: Query, filters: AmortizationFilters, model) -> Query:
    """
    Aplicar filtros a una query de amortizaciones
    
    Args:
        query: Query de SQLAlchemy
        filters: Filtros a aplicar
        model: Modelo de Amortization
        
    Returns:
        Query filtrada
    """
    # Filtros básicos
    if filters.company_id:
        query = query.filter(model.company_id == filters.company_id)
    
    if filters.is_active is not None:
        query = query.filter(model.is_active == filters.is_active)
    
    # Filtros específicos de amortización
    if filters.entity_id:
        query = query.filter(model.entity_id == filters.entity_id)
    
    if filters.status:
        query = query.filter(model.status == filters.status)
    
    if filters.amortization_method:
        query = query.filter(model.amortization_method == filters.amortization_method)
    
    if filters.frequency:
        query = query.filter(model.frequency == filters.frequency)
    
    # Filtros de fecha
    if filters.date_from:
        query = query.filter(model.start_date >= filters.date_from)
    
    if filters.date_to:
        query = query.filter(model.start_date <= filters.date_to)
    
    if filters.created_from:
        query = query.filter(model.created_at >= filters.created_from)
    
    if filters.created_to:
        query = query.filter(model.created_at <= filters.created_to)
    
    # Filtros de monto
    if filters.amount_from:
        query = query.filter(model.total_amount >= filters.amount_from)
    
    if filters.amount_to:
        query = query.filter(model.total_amount <= filters.amount_to)
    
    # Filtros de cuotas
    if filters.installments_from:
        query = query.filter(model.total_installments >= filters.installments_from)
    
    if filters.installments_to:
        query = query.filter(model.total_installments <= filters.installments_to)
    
    # Filtros booleanos especiales
    if filters.overdue_only:
        query = query.filter(model.status == 'overdue')
    
    if filters.completed_only:
        query = query.filter(model.status == 'completed')
    
    if filters.pending_only:
        query = query.filter(model.status.in_(['active', 'overdue']))
    
    # Filtro de búsqueda general
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.filter(
            or_(
                model.reference.ilike(search_term),
                model.description.ilike(search_term)
            )
        )
    
    # Filtro por nombre de entidad (requiere join)
    if filters.entity_name:
        from ..models.entity import Entity
        entity_search = f"%{filters.entity_name}%"
        query = query.join(Entity).filter(Entity.name.ilike(entity_search))
    
    # Filtro por tipo de entidad (requiere join)
    if filters.entity_type:
        from ..models.entity import Entity
        query = query.join(Entity).filter(Entity.type == filters.entity_type)
    
    return query

def apply_installment_filters(query: Query, filters: InstallmentFilters, model) -> Query:
    """
    Aplicar filtros a una query de cuotas
    
    Args:
        query: Query de SQLAlchemy
        filters: Filtros a aplicar
        model: Modelo de AmortizationInstallment
        
    Returns:
        Query filtrada
    """
    # Filtros básicos
    if filters.amortization_id:
        query = query.filter(model.amortization_id == filters.amortization_id)
    
    if filters.is_active is not None:
        query = query.filter(model.is_active == filters.is_active)
    
    # Filtros específicos de cuotas
    if filters.status:
        query = query.filter(model.status == filters.status)
    
    # Filtros de fecha de vencimiento
    if filters.due_date_from:
        query = query.filter(model.due_date >= filters.due_date_from)
    
    if filters.due_date_to:
        query = query.filter(model.due_date <= filters.due_date_to)
    
    # Filtros de fecha de pago
    if filters.payment_date_from:
        query = query.filter(model.payment_date >= filters.payment_date_from)
    
    if filters.payment_date_to:
        query = query.filter(model.payment_date <= filters.payment_date_to)
    
    # Filtros de monto
    if filters.amount_from:
        query = query.filter(model.total_amount >= filters.amount_from)
    
    if filters.amount_to:
        query = query.filter(model.total_amount <= filters.amount_to)
    
    # Filtros booleanos especiales
    if filters.overdue_only:
        today = date.today()
        query = query.filter(
            and_(
                model.status == 'pending',
                model.due_date < today
            )
        )
    
    if filters.paid_only:
        query = query.filter(model.status == 'paid')
    
    if filters.pending_only:
        query = query.filter(model.status.in_(['pending', 'partial']))
    
    # Filtro de búsqueda general
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.filter(model.notes.ilike(search_term))
    
    return query

def build_date_filter(field, date_from: Optional[date], date_to: Optional[date]):
    """Construir filtro de rango de fechas"""
    conditions = []
    
    if date_from:
        conditions.append(field >= date_from)
    
    if date_to:
        conditions.append(field <= date_to)
    
    if conditions:
        return and_(*conditions)
    
    return None

def build_amount_filter(field, amount_from: Optional[float], amount_to: Optional[float]):
    """Construir filtro de rango de montos"""
    conditions = []
    
    if amount_from is not None:
        conditions.append(field >= amount_from)
    
    if amount_to is not None:
        conditions.append(field <= amount_to)
    
    if conditions:
        return and_(*conditions)
    
    return None

def apply_search_filter(query: Query, search_term: str, search_fields: List[str]) -> Query:
    """
    Aplicar filtro de búsqueda en múltiples campos
    
    Args:
        query: Query de SQLAlchemy
        search_term: Término de búsqueda
        search_fields: Lista de campos donde buscar
        
    Returns:
        Query filtrada
    """
    if not search_term or not search_fields:
        return query
    
    search_pattern = f"%{search_term}%"
    conditions = [field.ilike(search_pattern) for field in search_fields]
    
    return query.filter(or_(*conditions))