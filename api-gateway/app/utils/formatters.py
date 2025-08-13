# api-gateway/app/utils/formatters.py
from typing import Optional, Union
from datetime import date, datetime
from decimal import Decimal
import locale

def format_currency(
    amount: Union[int, float, Decimal, str],
    currency: str = "EUR",
    locale_code: str = "es_ES"
) -> str:
    """
    Formatear monto como moneda
    
    Args:
        amount: Monto a formatear
        currency: Código de moneda (ISO 4217)
        locale_code: Código de locale
        
    Returns:
        String formateado como moneda
    """
    if amount is None:
        return "-"
    
    try:
        # Convertir a Decimal para precisión
        if isinstance(amount, str):
            amount = Decimal(amount)
        elif isinstance(amount, (int, float)):
            amount = Decimal(str(amount))
        
        # Configuraciones de formato por moneda
        currency_formats = {
            "EUR": {"symbol": "€", "position": "after", "decimals": 2},
            "USD": {"symbol": "$", "position": "before", "decimals": 2},
            "GBP": {"symbol": "£", "position": "before", "decimals": 2},
            "JPY": {"symbol": "¥", "position": "before", "decimals": 0},
            "CHF": {"symbol": "CHF", "position": "after", "decimals": 2},
            "ARS": {"symbol": "AR$", "position": "before", "decimals": 2},
        }
        
        config = currency_formats.get(currency, {"symbol": currency, "position": "after", "decimals": 2})
        
        # Formatear número
        if config["decimals"] == 0:
            formatted_amount = f"{amount:,.0f}".replace(",", ".")
        else:
            formatted_amount = f"{amount:,.2f}".replace(",", ".")
        
        # Aplicar símbolo de moneda
        if config["position"] == "before":
            return f"{config['symbol']} {formatted_amount}"
        else:
            return f"{formatted_amount} {config['symbol']}"
        
    except Exception:
        return str(amount)

def format_date(
    date_obj: Union[date, datetime, str],
    format_type: str = "short",
    locale_code: str = "es_ES"
) -> str:
    """
    Formatear fecha
    
    Args:
        date_obj: Fecha a formatear
        format_type: Tipo de formato (short, medium, long, iso)
        locale_code: Código de locale
        
    Returns:
        String con fecha formateada
    """
    if date_obj is None:
        return "-"
    
    try:
        # Convertir string a date si es necesario
        if isinstance(date_obj, str):
            if "T" in date_obj:  # ISO datetime
                date_obj = datetime.fromisoformat(date_obj.replace("Z", "+00:00"))
            else:  # ISO date
                date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()
        
        # Extraer fecha si es datetime
        if isinstance(date_obj, datetime):
            date_part = date_obj.date()
        else:
            date_part = date_obj
        
        # Formatos según tipo
        if format_type == "iso":
            return date_part.isoformat()
        elif format_type == "short":
            return date_part.strftime("%d/%m/%Y")
        elif format_type == "medium":
            return date_part.strftime("%d %b %Y")
        elif format_type == "long":
            months_es = {
                1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
                5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
                9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
            }
            month_name = months_es.get(date_part.month, date_part.strftime("%B"))
            return f"{date_part.day} de {month_name} de {date_part.year}"
        else:
            return date_part.strftime("%d/%m/%Y")
        
    except Exception:
        return str(date_obj)

def format_datetime(
    datetime_obj: Union[datetime, str],
    format_type: str = "short",
    include_seconds: bool = False
) -> str:
    """
    Formatear fecha y hora
    
    Args:
        datetime_obj: Datetime a formatear
        format_type: Tipo de formato
        include_seconds: Incluir segundos
        
    Returns:
        String con datetime formateado
    """
    if datetime_obj is None:
        return "-"
    
    try:
        # Convertir string a datetime si es necesario
        if isinstance(datetime_obj, str):
            datetime_obj = datetime.fromisoformat(datetime_obj.replace("Z", "+00:00"))
        
        if format_type == "iso":
            return datetime_obj.isoformat()
        elif format_type == "short":
            if include_seconds:
                return datetime_obj.strftime("%d/%m/%Y %H:%M:%S")
            else:
                return datetime_obj.strftime("%d/%m/%Y %H:%M")
        elif format_type == "medium":
            if include_seconds:
                return datetime_obj.strftime("%d %b %Y, %H:%M:%S")
            else:
                return datetime_obj.strftime("%d %b %Y, %H:%M")
        else:
            return datetime_obj.strftime("%d/%m/%Y %H:%M")
        
    except Exception:
        return str(datetime_obj)

def format_percentage(
    value: Union[int, float, Decimal],
    decimals: int = 2,
    include_symbol: bool = True
) -> str:
    """
    Formatear porcentaje
    
    Args:
        value: Valor a formatear
        decimals: Número de decimales
        include_symbol: Incluir símbolo %
        
    Returns:
        String con porcentaje formateado
    """
    if value is None:
        return "-"
    
    try:
        if isinstance(value, str):
            value = float(value)
        
        formatted = f"{value:.{decimals}f}"
        
        if include_symbol:
            return f"{formatted}%"
        else:
            return formatted
        
    except Exception:
        return str(value)

def format_number(
    value: Union[int, float, Decimal],
    decimals: Optional[int] = None,
    thousands_separator: bool = True
) -> str:
    """
    Formatear número
    
    Args:
        value: Número a formatear
        decimals: Número de decimales (None para automático)
        thousands_separator: Usar separador de miles
        
    Returns:
        String con número formateado
    """
    if value is None:
        return "-"
    
    try:
        if isinstance(value, str):
            value = Decimal(value)
        elif isinstance(value, (int, float)):
            value = Decimal(str(value))
        
        if decimals is None:
            # Determinar decimales automáticamente
            if value == int(value):
                decimals = 0
            else:
                decimals = 2
        
        if thousands_separator:
            if decimals == 0:
                return f"{value:,.0f}".replace(",", ".")
            else:
                return f"{value:,.{decimals}f}".replace(",", ".")
        else:
            if decimals == 0:
                return f"{value:.0f}"
            else:
                return f"{value:.{decimals}f}"
        
    except Exception:
        return str(value)

def format_file_size(size_bytes: int) -> str:
    """
    Formatear tamaño de archivo
    
    Args:
        size_bytes: Tamaño en bytes
        
    Returns:
        String con tamaño formateado
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"

def format_duration(seconds: Union[int, float]) -> str:
    """
    Formatear duración en formato legible
    
    Args:
        seconds: Duración en segundos
        
    Returns:
        String con duración formateada
    """
    if seconds is None:
        return "-"
    
    try:
        seconds = int(seconds)
        
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}m {secs}s"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}d {hours}h"
        
    except Exception:
        return str(seconds)

def format_phone(phone: str, country_code: str = "+34") -> str:
    """
    Formatear número de teléfono
    
    Args:
        phone: Número de teléfono
        country_code: Código de país
        
    Returns:
        String con teléfono formateado
    """
    if not phone:
        return "-"
    
    # Remover caracteres no numéricos excepto +
    cleaned = "".join(c for c in phone if c.isdigit() or c == "+")
    
    if not cleaned.startswith("+") and len(cleaned) >= 9:
        cleaned = country_code + " " + cleaned
    
    return cleaned

def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncar texto con sufijo
    
    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        suffix: Sufijo a agregar
        
    Returns:
        Texto truncado
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix