# api-gateway/tests/test_amortization.py
import pytest
from fastapi import status
from decimal import Decimal
from datetime import date

class TestAmortization:
    """Tests para gestión de amortizaciones"""

    def test_list_amortizations(self, authenticated_client, test_amortization):
        """Test de listado de amortizaciones"""
        response = authenticated_client.get(
            f"/amortizations/?company_id={test_amortization.company_id}"
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1

    def test_get_amortization_detail(self, authenticated_client, test_amortization):
        """Test de obtener detalle de amortización"""
        response = authenticated_client.get(f"/amortizations/{test_amortization.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_amortization.id
        assert data["reference"] == test_amortization.reference

    def test_create_amortization(self, authenticated_client, test_company, test_entity):
        """Test de creación de amortización"""
        amortization_data = {
            "company_id": test_company.id,
            "entity_id": test_entity.id,
            "reference": "NEW-AMORT-001",
            "description": "New test amortization",
            "total_amount": 5000.00,
            "total_installments": 6,
            "interest_rate": 3.0,
            "start_date": "2024-02-01",
            "amortization_method": "linear",
            "frequency": "monthly"
        }
        
        response = authenticated_client.post("/amortizations/", json=amortization_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["reference"] == amortization_data["reference"]
        assert float(data["total_amount"]) == amortization_data["total_amount"]

    def test_create_amortization_invalid_data(self, authenticated_client, test_company):
        """Test de creación de amortización con datos inválidos"""
        amortization_data = {
            "company_id": test_company.id,
            "entity_id": "invalid-entity-id",
            "reference": "",  # Referencia vacía
            "total_amount": -1000,  # Monto negativo
            "total_installments": 0  # Cuotas inválidas
        }
        
        response = authenticated_client.post("/amortizations/", json=amortization_data)
        
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_update_amortization(self, authenticated_client, test_amortization):
        """Test de actualización de amortización"""
        update_data = {
            "description": "Updated description",
            "interest_rate": 4.5
        }
        
        response = authenticated_client.put(
            f"/amortizations/{test_amortization.id}", 
            json=update_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == update_data["description"]
        assert float(data["interest_rate"]) == update_data["interest_rate"]

    def test_delete_amortization(self, authenticated_client, test_amortization):
        """Test de eliminación de amortización"""
        response = authenticated_client.delete(f"/amortizations/{test_amortization.id}")
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar que la amortización fue eliminada (soft delete)
        get_response = authenticated_client.get(f"/amortizations/{test_amortization.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_installments(self, authenticated_client, test_amortization, db_session):
        """Test de obtener cuotas de amortización"""
        # Crear algunas cuotas de test
        from app.models.amortization import AmortizationInstallment
        
        installment = AmortizationInstallment(
            amortization_id=test_amortization.id,
            installment_number=1,
            due_date=date(2024, 2, 1),
            principal_amount=Decimal("800.00"),
            interest_amount=Decimal("33.33"),
            total_amount=Decimal("833.33"),
            status="pending"
        )
        db_session.add(installment)
        db_session.commit()
        
        response = authenticated_client.get(
            f"/amortizations/{test_amortization.id}/installments"
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert data[0]["installment_number"] == 1

    def test_generate_installments(self, authenticated_client, test_amortization):
        """Test de generación de cuotas"""
        response = authenticated_client.post(
            f"/amortizations/{test_amortization.id}/generate-installments"
        )
        
        assert response.status_code == status.HTTP_200_OK

    def test_amortization_summary(self, authenticated_client, test_company):
        """Test de resumen de amortizaciones"""
        response = authenticated_client.get(
            f"/amortizations/reports/summary?company_id={test_company.id}"
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_amortizations" in data
        assert "total_amount" in data