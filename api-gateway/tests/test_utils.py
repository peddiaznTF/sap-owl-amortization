# api-gateway/tests/test_utils.py
import pytest
from app.utils.pagination import paginate
from app.utils.filters import AmortizationFilters
from sqlalchemy.orm import Session

class TestUtils:
    """Tests para utilidades"""

    def test_pagination(self, db_session, test_company):
        """Test de paginación"""
        from app.models.company import Company
        
        query = db_session.query(Company)
        result = paginate(query, page=1, page_size=10)
        
        assert "items" in result
        assert "total" in result
        assert "page" in result
        assert "page_size" in result

    def test_amortization_filters(self):
        """Test de filtros de amortización"""
        filters = AmortizationFilters(
            company_id="TEST001",
            entity_type="cliente",
            status="active"
        )
        
        assert filters.company_id == "TEST001"
        assert filters.entity_type == "cliente"
        assert filters.status == "active"

    def test_calculate_installments(self):
        """Test de cálculo de cuotas"""
        from app.services.amortization_service import AmortizationService
        
        service = AmortizationService()
        installments = service.calculate_linear_installments(
            total_amount=12000,
            installments=12,
            interest_rate=5.0,
            start_date="2024-01-01"
        )
        
        assert len(installments) == 12
        assert installments[0]["principal"] == 1000
        assert installments[0]["total"] > 1000  # Incluye interés
