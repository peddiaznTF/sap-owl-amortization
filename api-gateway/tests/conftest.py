# api-gateway/tests/conftest.py
import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import os
from typing import Generator

from app.main import app
from app.database import get_db, Base
from app.models.user import User
from app.models.company import Company
from app.models.entity import Entity
from app.models.amortization import Amortization, AmortizationInstallment
from app.services.auth_service import AuthService

# Configuración de base de datos de test
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/amortization_test_db"
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def setup_database():
    """Configurar base de datos de test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(setup_database):
    """Sesión de base de datos para tests"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """Cliente de test de FastAPI"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def auth_service():
    """Servicio de autenticación para tests"""
    return AuthService()

@pytest.fixture
def test_user(db_session, auth_service):
    """Usuario de test"""
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=auth_service.get_password_hash("testpassword"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def authenticated_client(client, test_user, auth_service):
    """Cliente autenticado para tests"""
    token = auth_service.create_access_token(
        data={"sub": test_user.email, "user_id": test_user.id}
    )
    client.headers = {"Authorization": f"Bearer {token}"}
    return client

@pytest.fixture
def test_company(db_session):
    """Compañía de test"""
    company = Company(
        id="TEST001",
        name="Test Company",
        currency="EUR",
        sap_database="TESTDB",
        description="Test company for unit tests"
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company

@pytest.fixture
def test_entity(db_session, test_company):
    """Entidad de test"""
    entity = Entity(
        company_id=test_company.id,
        sap_card_code="TEST001",
        name="Test Entity",
        type="cliente",
        currency="EUR"
    )
    db_session.add(entity)
    db_session.commit()
    db_session.refresh(entity)
    return entity

@pytest.fixture
def test_amortization(db_session, test_company, test_entity):
    """Amortización de test"""
    amortization = Amortization(
        company_id=test_company.id,
        entity_id=test_entity.id,
        reference="TEST-AMORT-001",
        description="Test amortization",
        total_amount=10000.00,
        pending_amount=10000.00,
        total_installments=12,
        installment_amount=833.33,
        interest_rate=5.0,
        start_date="2024-01-01",
        amortization_method="french",
        frequency="monthly"
    )
    db_session.add(amortization)
    db_session.commit()
    db_session.refresh(amortization)
    return amortization
