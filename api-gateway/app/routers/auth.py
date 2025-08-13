# api-gateway/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db
from ..services.auth_service import AuthService
from ..schemas.auth import UserCreate, UserLogin, Token, UserResponse
from ..schemas.common import MessageResponse

router = APIRouter()
security = HTTPBearer()
auth_service = AuthService()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Dependencia para obtener usuario actual"""
    return auth_service.get_current_user(db, credentials.credentials)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Registrar nuevo usuario"""
    try:
        user = auth_service.create_user(db, user_data)
        return UserResponse.from_orm(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login_user(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Iniciar sesión"""
    try:
        return auth_service.login_user(db, user_credentials)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during login: {str(e)}"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Renovar token de acceso"""
    try:
        return auth_service.refresh_token(db, credentials.credentials)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing token: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """Obtener información del usuario actual"""
    return UserResponse.from_orm(current_user)

@router.post("/logout", response_model=MessageResponse)
async def logout_user(
    current_user = Depends(get_current_user)
):
    """Cerrar sesión (invalidar token)"""
    # En una implementación completa, se debería mantener una lista negra de tokens
    # o usar un sistema de sesiones más sofisticado
    return MessageResponse(
        message="Successfully logged out",
        success=True
    )

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    current_password: str,
    new_password: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cambiar contraseña del usuario actual"""
    try:
        auth_service.change_password(db, current_user, current_password, new_password)
        return MessageResponse(
            message="Password changed successfully",
            success=True
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error changing password: {str(e)}"
        )

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    email: str,
    db: Session = Depends(get_db)
):
    """Solicitar reset de contraseña"""
    try:
        # Siempre retornar éxito por seguridad (no revelar si el email existe)
        auth_service.reset_password(db, email)
        return MessageResponse(
            message="If the email exists, a password reset link has been sent",
            success=True
        )
    except Exception as e:
        # Log error but don't expose it
        return MessageResponse(
            message="If the email exists, a password reset link has been sent",
            success=True
        )

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    token: str,
    new_password: str,
    db: Session = Depends(get_db)
):
    """Completar reset de contraseña"""
    try:
        auth_service.complete_password_reset(db, token, new_password)
        return MessageResponse(
            message="Password reset successfully",
            success=True
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting password: {str(e)}"
        )

@router.get("/verify-token")
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Verificar validez del token"""
    try:
        payload = auth_service.verify_token(credentials.credentials)
        return {
            "valid": True,
            "expires": payload.get("exp"),
            "user_id": payload.get("user_id")
        }
    except HTTPException:
        return {"valid": False}
