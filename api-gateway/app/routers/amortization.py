# # api-gateway/app/routers/amortization.py
# from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
# from sqlalchemy.orm import Session, joinedload
# from sqlalchemy import and_, or_, desc, asc
# from typing import List, Optional
# from datetime import date, datetime
# from decimal import Decimal

# from ..database import get_db
# from ..models.amortization import Amortization, AmortizationInstallment
# from ..models.entity import Entity
# from ..models.company import Company
# from ..schemas.amortization import (
#     AmortizationCreate, AmortizationUpdate, AmortizationResponse,
#     InstallmentCreate, InstallmentUpdate, InstallmentResponse,
#     AmortizationListResponse, AmortizationDetailResponse
# )
# from ..services.amortization_service import AmortizationService
# from ..services.sap_service import SAPService
# from ..utils.pagination import paginate
# from ..utils.filters import AmortizationFilters

# router = APIRouter()

# # Dependencias
# def get_amortization_service(db: Session = Depends(get_db)) -> AmortizationService:
#     return AmortizationService(db)

# def get_sap_service() -> SAPService:
#     return SAPService()

# @router.get("/", response_model=AmortizationListResponse)
# async def list_amortizations(
#     company_id: str = Query(..., description="ID de la compañía"),
#     entity_type: Optional[str] = Query(None, description="Tipo de entidad (cliente/proveedor)"),
#     status: Optional[str] = Query(None, description="Estado de la amortización"),
#     entity_name: Optional[str] = Query(None, description="Filtro por nombre de entidad"),
#     date_from: Optional[date] = Query(None, description="Fecha desde"),
#     date_to: Optional[date] = Query(None, description="Fecha hasta"),
#     overdue_only: Optional[bool] = Query(False, description="Solo amortizaciones vencidas"),
#     page: int = Query(1, ge=1),
#     page_size: int = Query(20, ge=1, le=100),
#     sort_by: str = Query("created_at", description="Campo para ordenar"),
#     sort_order: str = Query("desc", regex="^(asc|desc)$"),
#     db: Session = Depends(get_db),
#     amortization_service: AmortizationService = Depends(get_amortization_service)
# ):
#     """Listar amortizaciones con filtros y paginación"""
    
#     try:
#         # Crear filtros
#         filters = AmortizationFilters(
#             company_id=company_id,
#             entity_type=entity_type,
#             status=status,
#             entity_name=entity_name,
#             date_from=date_from,
#             date_to=date_to,
#             overdue_only=overdue_only
#         )
        
#         # Obtener amortizaciones
#         result = await amortization_service.list_amortizations(
#             filters=filters,
#             page=page,
#             page_size=page_size,
#             sort_by=sort_by,
#             sort_order=sort_order
#         )
        
#         return result
        
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error al obtener amortizaciones: {str(e)}"
#         )

# @router.get("/{amortization_id}", response_model=AmortizationDetailResponse)
# async def get_amortization(
#     amortization_id: str = Path(..., description="ID de la amortización"),
#     include_installments: bool = Query(True, description="Incluir cuotas"),
#     db: Session = Depends(get_db),
#     amortization_service: AmortizationService = Depends(get_amortization_service)
# ):
#     """Obtener detalles de una amortización específica"""
    
#     try:
#         amortization = await amortization_service.get_amortization_detail(
#             amortization_id=amortization_id,
#             include_installments=include_installments
#         )
        
#         if not amortization:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Amortización no encontrada"
#             )
        
#         return amortization
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error al obtener amortización: {str(e)}"
#         )

# @router.post("/", response_model=AmortizationResponse)
# async def create_amortization(
#     amortization_data: AmortizationCreate,
#     auto_generate_installments: bool = Query(True, description="Generar cuotas automáticamente"),
#     db: Session = Depends(get_db),
#     amortization_service: AmortizationService = Depends(get_amortization_service)
# ):
#     """Crear nueva amortización"""
    
#     try:
#         # Validar que la entidad existe
#         entity = db.query(Entity).filter(
#             and_(
#                 Entity.id == amortization_data.entity_id,
#                 Entity.company_id == amortization_data.company_id
#             )
#         ).first()
        
#         if not entity:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Entidad no encontrada"
#             )
        
#         # Crear amortización
#         amortization = await amortization_service.create_amortization(
#             amortization_data=amortization_data,
#             auto_generate_installments=auto_generate_installments
#         )
        
#         return amortization
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error al crear amortización: {str(e)}"
#         )

# @router.put("/{amortization_id}", response_model=AmortizationResponse)
# async def update_amortization(
#     amortization_id: str = Path(..., description="ID de la amortización"),
#     amortization_data: AmortizationUpdate = ...,
#     recalculate_installments: bool = Query(False, description="Recalcular cuotas"),
#     db: Session = Depends(get_db),
#     amortization_service: AmortizationService = Depends(get_amortization_service)
# ):
#     """Actualizar amortización existente"""
    
#     try:
#         amortization = await amortization_service.update_amortization(
#             amortization_id=amortization_id,
#             amortization_data=amortization_data,
#             recalculate_installments=recalculate_installments
#         )
        
#         if not amortization:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Amortización no encontrada"
#             )
        
#         return amortization
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error al actualizar amortización: {str(e)}"
#         )

# @router.delete("/{amortization_id}")
# async def delete_amortization(
#     amortization_id: str = Path(..., description="ID de la amortización"),
#     force_delete: bool = Query(False, description="Forzar eliminación"),
#     db: Session = Depends(get_db),
#     amortization_service: AmortizationService = Depends(get_amortization_service)
# ):
#     """Eliminar amortización (soft delete por defecto)"""
    
#     try:
#         success = await amortization_service.delete_amortization(
#             amortization_id=amortization_id,
#             force_delete=force_delete
#         )
        
#         if not success:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Amortización no encontrada"
#             )
        
#         return {"message": "Amortización eliminada exitosamente"}
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error al eliminar amortización: {str(e)}"
#         )

# # Endpoints para cuotas
# @router.get("/{amortization_id}/installments", response_model=List[InstallmentResponse])
# async def get_installments(
#     amortization_id: str = Path(..., description="ID de la amortización"),
#     status_filter: Optional[str] = Query(None, description="Filtrar por estado"),
#     overdue_only: bool = Query(False, description="Solo cuotas vencidas"),
#     db: Session = Depends(get_db),
#     amortization_service: AmortizationService = Depends(get_amortization_service)
# ):
#     """Obtener cuotas de una amortización"""
    
#     try:
#         installments = await amortization_service.get_installments(
#             amortization_id=amortization_id,
#             status_filter=status_filter,
#             overdue_only=overdue_only
#         )
        
#         return installments
        
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error al obtener cuotas: {str(e)}"
#         )

# @router.post("/{amortization_id}/installments/{installment_id}/pay")
# async def record_payment(
#     amortization_id: str = Path(..., description="ID de la amortización"),
#     installment_id: str = Path(..., description="ID de la cuota"),
#     payment_amount: Decimal = Query(..., description="Monto del pago"),
#     payment_date: Optional[date] = Query(None, description="Fecha del pago"),
#     notes: Optional[str] = Query(None, description="Notas del pago"),
#     create_sap_entry: bool = Query(True, description="Crear asiento en SAP"),
#     db: Session = Depends(get_db),
#     amortization_service: AmortizationService = Depends(get_amortization_service),
#     sap_service: SAPService = Depends(get_sap_service)
# ):
#     """Registrar pago de una cuota"""
    
#     try:
#         # Validar que la cuota pertenece a la amortización
#         installment = db.query(AmortizationInstallment).filter(
#             and_(
#                 AmortizationInstallment.id == installment_id,
#                 AmortizationInstallment.amortization_id == amortization_id
#             )
#         ).first()
        
#         if not installment:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Cuota no encontrada"
#             )
        
#         # Registrar pago
#         result = await amortization_service.record_payment(
#             installment_id=installment_id,
#             payment_amount=payment_amount,
#             payment_date=payment_date or date.today(),
#             notes=notes,
#             create_sap_entry=create_sap_entry,
#             sap_service=sap_service if create_sap_entry else None
#         )
        
#         return result
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error al registrar pago: {str(e)}"
#         )

# @router.post("/{amortization_id}/generate-installments")
# async def regenerate_installments(
#     amortization_id: str = Path(..., description="ID de la amortización"),
#     overwrite_existing: bool = Query(False, description="Sobrescribir cuotas existentes"),
#     db: Session = Depends(get_db),
#     amortization_service: AmortizationService = Depends(get_amortization_service)
# ):
#     """Regenerar tabla de cuotas"""
    
#     try:
#         result = await amortization_service.generate_installments(
#             amortization_id=amortization_id,
#             overwrite_existing=overwrite_existing
#         )
        
#         return result
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error al generar cuotas: {str(e)}"
#         )

# # Endpoints de integración SAP
# @router.post("/{amortization_id}/sync-to-sap")
# async def sync_to_sap(
#     amortization_id: str = Path(..., description="ID de la amortización"),
#     create_documents: bool = Query(True, description="Crear documentos en SAP"),
#     db: Session = Depends(get_db),
#     amortization_service: AmortizationService = Depends(get_amortization_service),
#     sap_service: SAPService = Depends(get_sap_service)
# ):
#     """Sincronizar amortización con SAP Business One"""
    
#     try:
#         amortization = db.query(Amortization).filter(
#             Amortization.id == amortization_id
#         ).first()
        
#         if not amortization:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Amortización no encontrada"
#             )
        
#         # Configurar SAP para la compañía
#         await sap_service.set_company(amortization.company_id)
        
#         # Sincronizar
#         result = await amortization_service.sync_to_sap(
#             amortization_id=amortization_id,
#             sap_service=sap_service,
#             create_documents=create_documents
#         )
        
#         return result
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error al sincronizar con SAP: {str(e)}"
#         )

# @router.post("/import-from-sap")
# async def import_from_sap(
#     company_id: str = Query(..., description="ID de la compañía"),
#     entity_type: str = Query(..., description="Tipo de entidad"),
#     document_types: List[str] = Query(["Invoices"], description="Tipos de documento"),
#     date_from: Optional[date] = Query(None, description="Fecha desde"),
#     date_to: Optional[date] = Query(None, description="Fecha hasta"),
#     auto_create_amortizations: bool = Query(False, description="Crear amortizaciones automáticamente"),
#     db: Session = Depends(get_db),
#     amortization_service: AmortizationService = Depends(get_amortization_service),
#     sap_service: SAPService = Depends(get_sap_service)
# ):
#     """Importar documentos de SAP para crear amortizaciones"""
    
#     try:
#         # Configurar SAP
#         await sap_service.set_company(company_id)
        
#         # Importar documentos
#         result = await amortization_service.import_from_sap(
#             company_id=company_id,
#             entity_type=entity_type,
#             document_types=document_types,
#             date_from=date_from,
#             date_to=date_to,
#             auto_create_amortizations=auto_create_amortizations,
#             sap_service=sap_service
#         )
        
#         return result
        
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error al importar desde SAP: {str(e)}"
#         )

# # Endpoints de reportes
# @router.get("/reports/summary")
# async def amortization_summary(
#     company_id: str = Query(..., description="ID de la compañía"),
#     entity_type: Optional[str] = Query(None, description="Tipo de entidad"),
#     status: Optional[str] = Query(None, description="Estado"),
#     date_from: Optional[date] = Query(None, description="Fecha desde"),
#     date_to: Optional[date] = Query(None, description="Fecha hasta"),
#     db: Session = Depends(get_db),
#     amortization_service: AmortizationService = Depends(get_amortization_service)
# ):
#     """Resumen de amortizaciones"""
    
#     try:
#         summary = await amortization_service.get_amortization_summary(
#             company_id=company_id,
#             entity_type=entity_type,
#             status=status,
#             date_from=date_from,
#             date_to=date_to
#         )
        
#         return summary
        
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error al obtener resumen: {str(e)}"
#         )

# @router.get("/reports/aging")
# async def aging_report(
#     company_id: str = Query(..., description="ID de la compañía"),
#     entity_type: Optional[str] = Query(None, description="Tipo de entidad"),
#     aging_periods: List[int] = Query([30, 60, 90, 120], description="Períodos de aging"),
#     db: Session = Depends(get_db),
#     amortization_service: AmortizationService = Depends(get_amortization_service)
# ):
#     """Reporte de aging de amortizaciones"""
    
#     try:
#         aging = await amortization_service.get_aging_report(
#             company_id=company_id,
#             entity_type=entity_type,
#             aging_periods=aging_periods
#         )
        
#         return aging
        
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error al generar reporte de aging: {str(e)}"
#         )

# api-gateway/app/routers/amortization.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

from ..database import get_db
from ..models.amortization import Amortization, AmortizationInstallment
from ..models.entity import Entity
from ..models.company import Company
from ..schemas.amortization import (
    AmortizationCreate, AmortizationUpdate, AmortizationResponse,
    InstallmentCreate, InstallmentUpdate, InstallmentResponse,
    AmortizationListResponse, AmortizationDetailResponse
)
from ..services.amortization_service import AmortizationService
from ..services.sap_service import SAPService
from ..utils.pagination import paginate
from ..utils.filters import AmortizationFilters

router = APIRouter()

# Dependencias
def get_amortization_service(db: Session = Depends(get_db)) -> AmortizationService:
    return AmortizationService(db)

def get_sap_service() -> SAPService:
    return SAPService()

@router.get("/", response_model=AmortizationListResponse)
async def list_amortizations(
    company_id: str = Query(..., description="ID de la compañía"),
    entity_type: Optional[str] = Query(None, description="Tipo de entidad (cliente/proveedor)"),
    status: Optional[str] = Query(None, description="Estado de la amortización"),
    entity_name: Optional[str] = Query(None, description="Filtro por nombre de entidad"),
    date_from: Optional[date] = Query(None, description="Fecha desde"),
    date_to: Optional[date] = Query(None, description="Fecha hasta"),
    overdue_only: Optional[bool] = Query(False, description="Solo amortizaciones vencidas"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", description="Campo para ordenar"),
    sort_order: str = Query("desc", description="Orden ascendente o descendente"),
    db: Session = Depends(get_db),
    amortization_service: AmortizationService = Depends(get_amortization_service)
):
    """Listar amortizaciones con filtros y paginación"""
    
    try:
        # Validar sort_order
        if sort_order not in ["asc", "desc"]:
            sort_order = "desc"
            
        # Crear filtros
        filters = AmortizationFilters(
            company_id=company_id,
            entity_type=entity_type,
            status=status,
            entity_name=entity_name,
            date_from=date_from,
            date_to=date_to,
            overdue_only=overdue_only
        )
        
        # Obtener amortizaciones
        result = await amortization_service.list_amortizations(
            filters=filters,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener amortizaciones: {str(e)}"
        )

@router.get("/{amortization_id}", response_model=AmortizationDetailResponse)
async def get_amortization(
    amortization_id: str = Path(..., description="ID de la amortización"),
    include_installments: bool = Query(True, description="Incluir cuotas"),
    db: Session = Depends(get_db),
    amortization_service: AmortizationService = Depends(get_amortization_service)
):
    """Obtener detalles de una amortización específica"""
    
    try:
        amortization = await amortization_service.get_amortization_detail(
            amortization_id=amortization_id,
            include_installments=include_installments
        )
        
        if not amortization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Amortización no encontrada"
            )
        
        return amortization
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener amortización: {str(e)}"
        )

@router.post("/", response_model=AmortizationResponse)
async def create_amortization(
    amortization_data: AmortizationCreate,
    auto_generate_installments: bool = Query(True, description="Generar cuotas automáticamente"),
    db: Session = Depends(get_db),
    amortization_service: AmortizationService = Depends(get_amortization_service)
):
    """Crear nueva amortización"""
    
    try:
        # Validar que la entidad existe
        entity = db.query(Entity).filter(
            and_(
                Entity.id == amortization_data.entity_id,
                Entity.company_id == amortization_data.company_id
            )
        ).first()
        
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entidad no encontrada"
            )
        
        # Crear amortización
        amortization = await amortization_service.create_amortization(
            amortization_data=amortization_data,
            auto_generate_installments=auto_generate_installments
        )
        
        return amortization
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear amortización: {str(e)}"
        )

@router.put("/{amortization_id}", response_model=AmortizationResponse)
async def update_amortization(
    amortization_id: str = Path(..., description="ID de la amortización"),
    amortization_data: AmortizationUpdate = ...,
    recalculate_installments: bool = Query(False, description="Recalcular cuotas"),
    db: Session = Depends(get_db),
    amortization_service: AmortizationService = Depends(get_amortization_service)
):
    """Actualizar amortización existente"""
    
    try:
        amortization = await amortization_service.update_amortization(
            amortization_id=amortization_id,
            amortization_data=amortization_data,
            recalculate_installments=recalculate_installments
        )
        
        if not amortization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Amortización no encontrada"
            )
        
        return amortization
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar amortización: {str(e)}"
        )

@router.delete("/{amortization_id}")
async def delete_amortization(
    amortization_id: str = Path(..., description="ID de la amortización"),
    force_delete: bool = Query(False, description="Forzar eliminación"),
    db: Session = Depends(get_db),
    amortization_service: AmortizationService = Depends(get_amortization_service)
):
    """Eliminar amortización (soft delete por defecto)"""
    
    try:
        success = await amortization_service.delete_amortization(
            amortization_id=amortization_id,
            force_delete=force_delete
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Amortización no encontrada"
            )
        
        return {"message": "Amortización eliminada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar amortización: {str(e)}"
        )

# Endpoints para cuotas
@router.get("/{amortization_id}/installments", response_model=List[InstallmentResponse])
async def get_installments(
    amortization_id: str = Path(..., description="ID de la amortización"),
    status_filter: Optional[str] = Query(None, description="Filtrar por estado"),
    overdue_only: bool = Query(False, description="Solo cuotas vencidas"),
    db: Session = Depends(get_db),
    amortization_service: AmortizationService = Depends(get_amortization_service)
):
    """Obtener cuotas de una amortización"""
    
    try:
        installments = await amortization_service.get_installments(
            amortization_id=amortization_id,
            status_filter=status_filter,
            overdue_only=overdue_only
        )
        
        return installments
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener cuotas: {str(e)}"
        )

@router.post("/{amortization_id}/installments/{installment_id}/pay")
async def record_payment(
    amortization_id: str = Path(..., description="ID de la amortización"),
    installment_id: str = Path(..., description="ID de la cuota"),
    payment_amount: Decimal = Query(..., description="Monto del pago"),
    payment_date: Optional[date] = Query(None, description="Fecha del pago"),
    notes: Optional[str] = Query(None, description="Notas del pago"),
    create_sap_entry: bool = Query(True, description="Crear asiento en SAP"),
    db: Session = Depends(get_db),
    amortization_service: AmortizationService = Depends(get_amortization_service)
):
    """Registrar pago de cuota"""
    
    try:
        result = await amortization_service.record_payment(
            amortization_id=amortization_id,
            installment_id=installment_id,
            payment_amount=payment_amount,
            payment_date=payment_date or date.today(),
            notes=notes,
            create_sap_entry=create_sap_entry
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar pago: {str(e)}"
        )