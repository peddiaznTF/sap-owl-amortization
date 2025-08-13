# api-gateway/app/utils/pagination.py
from typing import List, Any, Dict, Optional
from sqlalchemy.orm import Query
from sqlalchemy import func, desc, asc
from pydantic import BaseModel
import math

class PaginatedResult(BaseModel):
    """Resultado paginado genérico"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool
    total_pages: int
    
    class Config:
        arbitrary_types_allowed = True

def paginate(
    query: Query,
    page: int = 1,
    page_size: int = 20,
    sort_by: Optional[str] = None,
    sort_order: str = "desc",
    max_page_size: int = 100
) -> Dict[str, Any]:
    """
    Paginar una query de SQLAlchemy
    
    Args:
        query: Query de SQLAlchemy
        page: Número de página (empezando en 1)
        page_size: Elementos por página
        sort_by: Campo para ordenar
        sort_order: Orden (asc/desc)
        max_page_size: Tamaño máximo de página
        
    Returns:
        Dict con datos paginados
    """
    # Validar parámetros
    page = max(1, page)
    page_size = min(max(1, page_size), max_page_size)
    
    # Obtener total de elementos
    total = query.count()
    
    # Calcular offset
    offset = (page - 1) * page_size
    
    # Aplicar ordenamiento si se especifica
    if sort_by:
        try:
            # Obtener el modelo de la query
            model = query.column_descriptions[0]['type']
            
            # Verificar que el campo existe en el modelo
            if hasattr(model, sort_by):
                sort_field = getattr(model, sort_by)
                
                if sort_order.lower() == "asc":
                    query = query.order_by(asc(sort_field))
                else:
                    query = query.order_by(desc(sort_field))
        except (IndexError, AttributeError):
            # Si hay error, aplicar ordenamiento por defecto
            pass
    
    # Aplicar paginación
    items = query.offset(offset).limit(page_size).all()
    
    # Calcular metadatos de paginación
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_next": has_next,
        "has_prev": has_prev,
        "total_pages": total_pages
    }

def paginate_list(
    items_list: List[Any],
    page: int = 1,
    page_size: int = 20,
    max_page_size: int = 100
) -> Dict[str, Any]:
    """
    Paginar una lista en memoria
    
    Args:
        items_list: Lista de elementos
        page: Número de página
        page_size: Elementos por página
        max_page_size: Tamaño máximo de página
        
    Returns:
        Dict con datos paginados
    """
    # Validar parámetros
    page = max(1, page)
    page_size = min(max(1, page_size), max_page_size)
    
    total = len(items_list)
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    # Calcular índices
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    # Obtener elementos de la página
    items = items_list[start_idx:end_idx]
    
    # Calcular metadatos
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_next": has_next,
        "has_prev": has_prev,
        "total_pages": total_pages
    }

class PaginationParams(BaseModel):
    """Parámetros de paginación para validación"""
    page: int = 1
    page_size: int = 20
    sort_by: Optional[str] = None
    sort_order: str = "desc"
    
    class Config:
        validate_assignment = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validaciones adicionales
        self.page = max(1, self.page)
        self.page_size = min(max(1, self.page_size), 100)
        if self.sort_order not in ["asc", "desc"]:
            self.sort_order = "desc"

def get_pagination_info(total: int, page: int, page_size: int) -> Dict[str, Any]:
    """
    Obtener información de paginación sin realizar query
    
    Args:
        total: Total de elementos
        page: Página actual
        page_size: Elementos por página
        
    Returns:
        Dict con información de paginación
    """
    page = max(1, page)
    page_size = max(1, page_size)
    
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_next": has_next,
        "has_prev": has_prev,
        "total_pages": total_pages,
        "start_item": ((page - 1) * page_size) + 1 if total > 0 else 0,
        "end_item": min(page * page_size, total)
    }

def build_pagination_links(
    base_url: str,
    page: int,
    total_pages: int,
    query_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Optional[str]]:
    """
    Construir enlaces de paginación
    
    Args:
        base_url: URL base
        page: Página actual
        total_pages: Total de páginas
        query_params: Parámetros adicionales para la URL
        
    Returns:
        Dict con enlaces de paginación
    """
    if query_params is None:
        query_params = {}
    
    def build_url(page_num: int) -> str:
        params = {**query_params, "page": page_num}
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_str}"
    
    links = {
        "first": build_url(1) if total_pages > 0 else None,
        "last": build_url(total_pages) if total_pages > 0 else None,
        "prev": build_url(page - 1) if page > 1 else None,
        "next": build_url(page + 1) if page < total_pages else None,
        "current": build_url(page)
    }
    
    return links