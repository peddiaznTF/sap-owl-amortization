# api-gateway/app/database.py
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging
from typing import Generator

from .config import settings

logger = logging.getLogger(__name__)

# Configuración del motor de base de datos
engine_config = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "echo": settings.DEBUG,  # Log SQL queries en modo debug
}

# Configurar motor según el tipo de base de datos
if settings.DATABASE_URL.startswith("sqlite"):
    # Configuración especial para SQLite (desarrollo/testing)
    engine_config.update({
        "poolclass": StaticPool,
        "connect_args": {
            "check_same_thread": False,
            "timeout": 20,
        }
    })
elif settings.DATABASE_URL.startswith("postgresql"):
    # Configuración para PostgreSQL (producción)
    engine_config.update({
        "pool_size": 20,
        "max_overflow": 0,
        "connect_args": {
            "connect_timeout": 10,
            "application_name": "sap_amortization_api",
        }
    })

# Crear motor de base de datos
engine = create_engine(settings.DATABASE_URL, **engine_config)

# Configurar SessionLocal
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# Base para modelos
Base = declarative_base()

# Event listeners para optimización
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Configurar pragma para SQLite"""
    if settings.DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        # Configuraciones de performance para SQLite
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=1000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()

@event.listens_for(engine, "connect")
def set_postgresql_config(dbapi_connection, connection_record):
    """Configurar parámetros para PostgreSQL"""
    if settings.DATABASE_URL.startswith("postgresql"):
        cursor = dbapi_connection.cursor()
        # Configuraciones de timezone y encoding
        cursor.execute("SET timezone TO 'UTC'")
        cursor.execute("SET client_encoding TO 'UTF8'")
        cursor.close()

# Dependencia para obtener sesión de base de datos
def get_db() -> Generator[Session, None, None]:
    """
    Dependencia de FastAPI para obtener sesión de base de datos.
    Garantiza que la sesión se cierre correctamente.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Función para crear todas las tablas
def create_tables():
    """Crear todas las tablas en la base de datos"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

# Función para verificar conexión a base de datos
def check_database_connection() -> bool:
    """Verificar que la conexión a la base de datos funciona"""
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

# Función para obtener información de la base de datos
def get_database_info() -> dict:
    """Obtener información sobre la base de datos"""
    try:
        with engine.connect() as connection:
            if settings.DATABASE_URL.startswith("postgresql"):
                result = connection.execute("SELECT version()")
                version = result.fetchone()[0]
                db_type = "PostgreSQL"
            elif settings.DATABASE_URL.startswith("sqlite"):
                result = connection.execute("SELECT sqlite_version()")
                version = result.fetchone()[0]
                db_type = "SQLite"
            else:
                version = "Unknown"
                db_type = "Unknown"
            
            return {
                "type": db_type,
                "version": version,
                "url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "local",
                "connected": True
            }
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        return {
            "type": "Unknown",
            "version": "Unknown", 
            "url": "Unknown",
            "connected": False,
            "error": str(e)
        }

# Context manager para transacciones
class DatabaseTransaction:
    """Context manager para manejo de transacciones"""
    
    def __init__(self):
        self.db = None
    
    def __enter__(self) -> Session:
        self.db = SessionLocal()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.db.rollback()
            logger.error(f"Transaction rolled back due to: {exc_val}")
        else:
            self.db.commit()
        self.db.close()

# Función para ejecutar con retry
def execute_with_retry(func, max_retries=3, *args, **kwargs):
    """Ejecutar función con reintentos en caso de error de base de datos"""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Database operation failed (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                logger.error(f"Database operation failed after {max_retries} attempts")
                raise
            # Pequeña pausa antes del reintento
            import time
            time.sleep(0.1 * (attempt + 1))

# Inicialización
def init_database():
    """Inicializar la base de datos"""
    logger.info("Initializing database...")
    
    # Verificar conexión
    if not check_database_connection():
        raise Exception("Cannot connect to database")
    
    # Crear tablas
    create_tables()
    
    # Log información de la base de datos
    db_info = get_database_info()
    logger.info(f"Database initialized: {db_info['type']} {db_info['version']}")

if __name__ == "__main__":
    # Para testing directo
    init_database()
    print("Database configuration loaded successfully")