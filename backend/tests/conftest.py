import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app

engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(bind=engine)

'''
@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    session.close()
    Base.metadata.drop_all(bind=engine)
'''

@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_headers(client, db_session):
    from app.auth import hash_password
    from app.models import User

    user = User(email="admin@test.com", password_hash=hash_password("testpass123"), role="admin")
    db_session.add(user)
    db_session.commit()
    token = client.post(
        "/api/auth/login", data={"username": "admin@test.com", "password": "testpass123"}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}