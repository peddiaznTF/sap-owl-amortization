# api-gateway/tests/test_sap_integration.py
import pytest
from unittest.mock import Mock, patch
from fastapi import status

class TestSAPIntegration:
    """Tests para integración con SAP"""

    @patch('app.services.sap_service.SAPService')
    def test_sap_connection(self, mock_sap_service, authenticated_client):
        """Test de conexión con SAP"""
        mock_sap_service.return_value.test_connection.return_value = {
            "status": "connected",
            "company": "TEST001"
        }
        
        response = authenticated_client.post("/sap/test-connection", json={
            "company": "TEST001"
        })
        
        assert response.status_code == status.HTTP_200_OK

    @patch('app.services.sap_service.SAPService')
    def test_sync_business_partners(self, mock_sap_service, authenticated_client, test_company):
        """Test de sincronización de business partners"""
        mock_sap_service.return_value.get_business_partners.return_value = [
            {
                "CardCode": "C001",
                "CardName": "Test Customer",
                "CardType": "C"
            }
        ]
        
        response = authenticated_client.post("/sap/sync-business-partners", json={
            "company_id": test_company.id,
            "entity_type": "cliente"
        })
        
        assert response.status_code == status.HTTP_200_OK

    @patch('app.services.sap_service.SAPService')
    def test_import_documents(self, mock_sap_service, authenticated_client, test_company):
        """Test de importación de documentos SAP"""
        mock_sap_service.return_value.get_pending_documents.return_value = [
            {
                "DocEntry": 1,
                "DocNum": 1001,
                "CardCode": "C001",
                "DocTotal": 5000.00
            }
        ]
        
        response = authenticated_client.post("/sap/import-documents", json={
            "company_id": test_company.id,
            "document_types": ["Invoices"],
            "auto_create_amortizations": False
        })
        
        assert response.status_code == status.HTTP_200_OK
