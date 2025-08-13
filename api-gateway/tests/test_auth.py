# api-gateway/tests/test_auth.py
import pytest
from fastapi import status
from app.models.user import User

class TestAuth:
    """Tests para autenticación"""

    def test_register_user_success(self, client, db_session):
        """Test de registro exitoso"""
        user_data = {
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "newpassword123",
            "confirm_password": "newpassword123",
            "is_active": True
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
        
        # Verificar que el usuario se creó en la base de datos
        user = db_session.query(User).filter(User.email == user_data["email"]).first()
        assert user is not None

    def test_register_user_duplicate_email(self, client, test_user):
        """Test de registro con email duplicado"""
        user_data = {
            "email": test_user.email,
            "full_name": "Another User",
            "password": "password123",
            "confirm_password": "password123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_user_password_mismatch(self, client):
        """Test de registro con contraseñas que no coinciden"""
        user_data = {
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "password123",
            "confirm_password": "differentpassword"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_success(self, client, test_user):
        """Test de login exitoso"""
        login_data = {
            "email": test_user.email,
            "password": "testpassword"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

    def test_login_wrong_password(self, client, test_user):
        """Test de login con contraseña incorrecta"""
        login_data = {
            "email": test_user.email,
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, client):
        """Test de login con usuario inexistente"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user(self, authenticated_client, test_user):
        """Test de obtener usuario actual"""
        response = authenticated_client.get("/auth/me")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name

    def test_get_current_user_unauthorized(self, client):
        """Test de obtener usuario sin autenticación"""
        response = client.get("/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token(self, authenticated_client):
        """Test de renovación de token"""
        response = authenticated_client.post("/auth/refresh")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_change_password_success(self, authenticated_client, test_user, db_session):
        """Test de cambio de contraseña exitoso"""
        response = authenticated_client.post("/auth/change-password", params={
            "current_password": "testpassword",
            "new_password": "newpassword123"
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar que la contraseña cambió
        db_session.refresh(test_user)
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        assert auth_service.verify_password("newpassword123", test_user.hashed_password)

    def test_change_password_wrong_current(self, authenticated_client):
        """Test de cambio de contraseña con contraseña actual incorrecta"""
        response = authenticated_client.post("/auth/change-password", params={
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_forgot_password(self, client, test_user):
        """Test de solicitud de reset de contraseña"""
        response = client.post("/auth/forgot-password", params={
            "email": test_user.email
        })
        
        assert response.status_code == status.HTTP_200_OK

    def test_verify_token_valid(self, authenticated_client):
        """Test de verificación de token válido"""
        response = authenticated_client.get("/auth/verify-token")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is True

    def test_verify_token_invalid(self, client):
        """Test de verificación de token inválido"""
        client.headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/verify-token")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is False
