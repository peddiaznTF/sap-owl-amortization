# api-gateway/app/schemas/common.py
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional, Any, Dict
from datetime import datetime

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Schema genérico para respuestas paginadas"""
    items: List[T]
    total: int = Field(..., description="Total de elementos")
    page: int = Field(..., ge=1, description="Página actual")
    page_size: int = Field(..., ge=1, le=100, description="Elementos por página")
    has_next: bool = Field(..., description="Hay página siguiente")
    has_prev: bool = Field(..., description="Hay página anterior")
    total_pages: int = Field(..., description="Total de páginas")

class MessageResponse(BaseModel):
    """Schema para respuestas con mensaje"""
    message: str = Field(..., description="Mensaje de respuesta")
    success: bool = Field(default=True, description="Operación exitosa")
    data: Optional[Dict[str, Any]] = Field(None, description="Datos adicionales")

class ErrorResponse(BaseModel):
    """Schema para respuestas de error"""
    error: bool = Field(default=True, description="Es un error")
    status_code: int = Field(..., description="Código de estado HTTP")
    message: str = Field(..., description="Mensaje de error")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalles del error")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del error")

class HealthResponse(BaseModel):
    """Schema para health check"""
    status: str = Field(..., description="Estado del servicio")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del check")
    services: Dict[str, str] = Field(..., description="Estado de servicios dependientes")
    version: str = Field(default="1.0.0", description="Versión de la API")

class FilterParams(BaseModel):
    """Schema base para parámetros de filtrado"""
    page: int = Field(default=1, ge=1, description="Número de página")
    page_size: int = Field(default=20, ge=1, le=100, description="Elementos por página")
    sort_by: str = Field(default="created_at", description="Campo para ordenar")
    sort_order: str = Field(default="desc", regex="^(asc|desc)$", description="Orden ascendente o descendente")
    search: Optional[str] = Field(None, max_length=255, description="Término de búsqueda")

class DateRangeFilter(BaseModel):
    """Schema para filtros de rango de fechas"""
    date_from: Optional[datetime] = Field(None, description="Fecha desde")
    date_to: Optional[datetime] = Field(None, description="Fecha hasta")
    
    @validator('date_to')
    def validate_date_range(cls, v, values):
        if v and 'date_from' in values and values['date_from']:
            if v < values['date_from']:
                raise ValueError('date_to must be greater than date_from')
        return v

class BulkOperationRequest(BaseModel):
    """Schema para operaciones en lote"""
    ids: List[str] = Field(..., min_items=1, max_items=100, description="Lista de IDs")
    operation: str = Field(..., description="Tipo de operación")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parámetros adicionales")

class BulkOperationResponse(BaseModel):
    """Schema para respuesta de operaciones en lote"""
    total_requested: int = Field(..., description="Total de elementos solicitados")
    successful: int = Field(..., description="Operaciones exitosas")
    failed: int = Field(..., description="Operaciones fallidas")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Lista de errores")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Resultados exitosos")

class ExportRequest(BaseModel):
    """Schema para solicitudes de exportación"""
    format: str = Field(..., regex="^(excel|csv|pdf)$", description="Formato de exportación")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filtros aplicados")
    include_headers: bool = Field(default=True, description="Incluir encabezados")
    date_format: str = Field(default="YYYY-MM-DD", description="Formato de fecha")

class ImportRequest(BaseModel):
    """Schema para solicitudes de importación"""
    file_data: str = Field(..., description="Datos del archivo en base64")
    file_type: str = Field(..., regex="^(excel|csv)$", description="Tipo de archivo")
    has_headers: bool = Field(default=True, description="El archivo tiene encabezados")
    mapping: Dict[str, str] = Field(..., description="Mapeo de columnas")
    validate_only: bool = Field(default=False, description="Solo validar, no importar")

class ImportResponse(BaseModel):
    """Schema para respuesta de importación"""
    total_rows: int = Field(..., description="Total de filas procesadas")
    successful_imports: int = Field(..., description="Importaciones exitosas")
    failed_imports: int = Field(..., description="Importaciones fallidas")
    validation_errors: List[Dict[str, Any]] = Field(default_factory=list, description="Errores de validación")
    imported_ids: List[str] = Field(default_factory=list, description="IDs de elementos importados")

# Configurar referencias circulares
from .amortization import AmortizationDetailResponse
from .installment import InstallmentResponse

AmortizationDetailResponse.model_rebuild()