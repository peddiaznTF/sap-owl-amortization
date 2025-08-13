# api-gateway/tests/test_companies.py
import pytest
from fastapi import status

class TestCompanies:
    """Tests para gestión de compañías"""

    def test_list_companies(self, authenticated_client, test_company):
        """Test de listado de compañías"""
        response = authenticated_client.get("/companies/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "companies" in data
        assert len(data["companies"]) >= 1

    def test_get_company(self, authenticated_client, test_company):
        """Test de obtener compañía específica"""
        response = authenticated_client.get(f"/companies/{test_company.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_company.id
        assert data["name"] == test_company.name

    def test_create_company(self, authenticated_client):
        """Test de creación de compañía"""
        company_data = {
            "id": "NEW001",
            "name": "New Test Company",
            "currency": "USD",
            "sap_database": "NEWDB",
            "description": "New test company"
        }
        
        response = authenticated_client.post("/companies/", json=company_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == company_data["id"]
        assert data["name"] == company_data["name"]

    def test_create_company_duplicate_id(self, authenticated_client, test_company):
        """Test de creación de compañía con ID duplicado"""
        company_data = {
            "id": test_company.id,
            "name": "Duplicate Company",
            "currency": "EUR",
            "sap_database": "DUPDB"
        }
        
        response = authenticated_client.post("/companies/", json=company_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_company(self, authenticated_client, test_company):
        """Test de actualización de compañía"""
        update_data = {
            "name": "Updated Test Company",
            "description": "Updated description"
        }
        
        response = authenticated_client.put(
            f"/companies/{test_company.id}", 
            json=update_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]

    def test_delete_company(self, authenticated_client, test_company):
        """Test de eliminación de compañía"""
        response = authenticated_client.delete(f"/companies/{test_company.id}")
        
        assert response.status_code == status.HTTP_200_OK
