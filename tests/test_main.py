from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
import pytest

from app.main import app, get_db
from app.database import Base

# Configuração de banco em memória para testes rápidos
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_task():
    response = client.post(
        "/tasks/",
        json={"title": "Test Task", "description": "Description here"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Description here"
    assert data["completed"] == False
    assert "id" in data

def test_read_tasks():
    # Cria uma tarefa primeiro
    client.post("/tasks/", json={"title": "Task 1"})
    
    response = client.get("/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Task 1"

def test_read_task_by_id():
    create_response = client.post("/tasks/", json={"title": "Task ID"})
    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Task ID"

def test_read_task_not_found():
    response = client.get("/tasks/999")
    assert response.status_code == 404

def test_update_task():
    create_response = client.post("/tasks/", json={"title": "Old Task"})
    task_id = create_response.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        json={"title": "New Task", "completed": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Task"
    assert data["completed"] == True

def test_delete_task():
    create_response = client.post("/tasks/", json={"title": "To Delete"})
    task_id = create_response.json()["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    # Verifica se foi deletado
    response_get = client.get(f"/tasks/{task_id}")
    assert response_get.status_code == 404
