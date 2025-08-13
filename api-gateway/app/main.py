# api-gateway/app/main.py
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
import uvicorn
from datetime import datetime

from .config import settings
from .database import engine, SessionLocal
from .models import Base
from .routers import amortization, companies, sap_integration, auth, reports
from .services.auth_service import AuthService
from .services.logging_service import setup_logging

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)

# Configurar contexto de la aplicación
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("Iniciando API Gateway para Sistema de Amortización")
    
    # Crear tablas de base de datos
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas de base de datos creadas/verificadas")
    
    yield
    
    # Shutdown
    logger.info("Cerrando API Gateway")

# Crear instancia de FastAPI
app = FastAPI(
    title="SAP Amortization Management API",
    description="API Gateway para Sistema Híbrido SAP Business One + OWL de Gestión de Amortización Financiera",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Configurar TrustedHost (para producción)
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# Configurar seguridad
security = HTTPBearer()
auth_service = AuthService()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependencia para autenticación"""
    try:
        payload = auth_service.verify_token(credentials.credentials)
        return payload
    except Exception as e:
        logger.error(f"Error de autenticación: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.now()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # Log response
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    return response

# Rutas principales
@app.get("/", tags=["Health"])
async def root():
    """Endpoint raíz"""
    return {
        "message": "SAP Amortization Management API",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        # Verificar conexión a base de datos
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": "connected",
                "api": "running"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )

@app.get("/info", tags=["Health"])
async def app_info():
    """Información de la aplicación"""
    return {
        "name": "SAP Amortization Management API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "features": [
            "Multi-company support",
            "SAP Business One integration",
            "Amortization table management",
            "Financial reporting",
            "Real-time synchronization"
        ],
        "endpoints": {
            "auth": "/auth",
            "companies": "/companies",
            "amortizations": "/amortizations",
            "sap": "/sap",
            "reports": "/reports"
        }
    }

# Incluir routers
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    companies.router,
    prefix="/companies",
    tags=["Companies"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    amortization.router,
    prefix="/amortizations",
    tags=["Amortizations"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    sap_integration.router,
    prefix="/sap",
    tags=["SAP Integration"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    reports.router,
    prefix="/reports",
    tags=["Reports"],
    dependencies=[Depends(get_current_user)]
)

# Manejadores de errores globales
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "message": "Error interno del servidor",
            "timestamp": datetime.now().isoformat()
        }
    )

# Ejecutar aplicación
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )