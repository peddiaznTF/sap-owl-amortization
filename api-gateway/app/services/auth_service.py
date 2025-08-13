# api-gateway/app/services/auth_service.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

from ..config import settings
from ..models.user import User
from ..schemas.auth import UserCreate, UserLogin, Token, UserResponse

logger = logging.getLogger(__name__)

class AuthService:
    """Servicio de autenticación y autorización"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generar hash de contraseña"""
        return self.pwd_context.hash(password)

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Crear token de acceso JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verificar y decodificar token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.warning(f"Token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Autenticar usuario con email y contraseña"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_user(self, db: Session, user_create: UserCreate) -> User:
        """Crear nuevo usuario"""
        # Verificar si el usuario ya existe
        existing_user = db.query(User).filter(User.email == user_create.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Crear nuevo usuario
        hashed_password = self.get_password_hash(user_create.password)
        db_user = User(
            email=user_create.email,
            full_name=user_create.full_name,
            hashed_password=hashed_password,
            is_active=user_create.is_active
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"New user created: {user_create.email}")
        return db_user

    def login_user(self, db: Session, user_login: UserLogin) -> Token:
        """Iniciar sesión de usuario"""
        user = self.authenticate_user(db, user_login.email, user_login.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )

        # Crear token de acceso
        access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
        access_token = self.create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )

        # Actualizar último login
        user.last_login = datetime.utcnow()
        db.commit()

        logger.info(f"User logged in: {user.email}")

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60,
            user=UserResponse.from_orm(user)
        )

    def get_current_user(self, db: Session, token: str) -> User:
        """Obtener usuario actual desde token"""
        try:
            payload = self.verify_token(token)
            email: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            
            if email is None or user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials"
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )

        return user

    def refresh_token(self, db: Session, current_token: str) -> Token:
        """Renovar token de acceso"""
        try:
            payload = self.verify_token(current_token)
            email: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            
            if email is None or user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials"
                )

            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )

            # Crear nuevo token
            access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
            access_token = self.create_access_token(
                data={"sub": user.email, "user_id": user.id},
                expires_delta=access_token_expires
            )

            return Token(
                access_token=access_token,
                token_type="bearer",
                expires_in=self.access_token_expire_minutes * 60,
                user=UserResponse.from_orm(user)
            )

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

    def change_password(self, db: Session, user: User, current_password: str, new_password: str) -> bool:
        """Cambiar contraseña de usuario"""
        if not self.verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        user.hashed_password = self.get_password_hash(new_password)
        db.commit()
        
        logger.info(f"Password changed for user: {user.email}")
        return True

    def reset_password(self, db: Session, email: str) -> str:
        """Generar token para reset de contraseña"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # No revelar si el email existe o no por seguridad
            logger.warning(f"Password reset attempted for non-existent email: {email}")
            return "reset_token_placeholder"

        # Crear token especial para reset (expira en 30 minutos)
        reset_token_expires = timedelta(minutes=30)
        reset_token = self.create_access_token(
            data={"sub": user.email, "user_id": user.id, "type": "password_reset"},
            expires_delta=reset_token_expires
        )

        # Aquí se debería enviar email con el token
        # TODO: Implementar servicio de email
        
        logger.info(f"Password reset token generated for user: {email}")
        return reset_token

    def validate_reset_token(self, token: str) -> Dict[str, Any]:
        """Validar token de reset de contraseña"""
        try:
            payload = self.verify_token(token)
            if payload.get("type") != "password_reset":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid reset token"
                )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )

    def complete_password_reset(self, db: Session, token: str, new_password: str) -> bool:
        """Completar reset de contraseña"""
        payload = self.validate_reset_token(token)
        user_id = payload.get("user_id")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found"
            )

        user.hashed_password = self.get_password_hash(new_password)
        db.commit()
        
        logger.info(f"Password reset completed for user: {user.email}")
        return True
