# api-gateway/app/services/logging_service.py
import logging
import logging.config
import json
from datetime import datetime
from typing import Dict, Any
import sys

from ..config import settings

class JSONFormatter(logging.Formatter):
    """Formateador JSON para logs"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Agregar información adicional si está disponible
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
            
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
            
        if hasattr(record, 'company_id'):
            log_data['company_id'] = record.company_id
            
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
            
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
            
        return json.dumps(log_data, ensure_ascii=False)

def setup_logging():
    """Configurar sistema de logging"""
    
    if settings.LOG_FORMAT.lower() == "json":
        formatter_class = "app.services.logging_service.JSONFormatter"
        format_string = ""
    else:
        formatter_class = "logging.Formatter"
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "class": formatter_class,
                "format": format_string,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "default",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "default",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
        },
        "loggers": {
            "app": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console"],
        },
    }
    
    # Crear directorio de logs si no existe
    import os
    os.makedirs("logs", exist_ok=True)
    
    logging.config.dictConfig(config)

class ContextualLogger:
    """Logger con contexto adicional"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context: Dict[str, Any] = {}
    
    def set_context(self, **kwargs):
        """Establecer contexto para todos los logs"""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Limpiar contexto"""
        self.context.clear()
    
    def _log_with_context(self, level: int, message: str, **kwargs):
        """Log con contexto adicional"""
        extra_data = {**self.context, **kwargs}
        extra = {"extra_data": extra_data} if extra_data else {}
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        self._log_with_context(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log_with_context(logging.CRITICAL, message, **kwargs)

def get_logger(name: str) -> ContextualLogger:
    """Obtener logger contextual"""
    return ContextualLogger(name)