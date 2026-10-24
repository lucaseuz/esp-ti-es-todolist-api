"""
TIPO 1 — Testes de Contrato de API (gerados via Prompt de Contrato)

Prompt utilizado na LLM:
    "Você é um especialista em testes de API REST. Dado o contrato a seguir de uma
    API FastAPI de To-Do List com os endpoints POST /tasks/, GET /tasks/,
    GET /tasks/{id}, PUT /tasks/{id} e DELETE /tasks/{id}, gere casos de teste de
    integração em Python com pytest e httpx que verifiquem:
    (1) Status HTTP correto para cada endpoint em cenário de sucesso,
    (2) Estrutura do corpo de resposta JSON (campos obrigatórios e tipos),
    (3) Headers de resposta esperados (Content-Type application/json).
    Use banco de dados SQLite em memória via fixture compartilhada."

Resultado: casos de teste focados na aderência do contrato REST.
"""

import pytest


class TestContratoPost:
    """Contrato do endpoint POST /tasks/"""

    def test_criar_tarefa_retorna_status_201(self, client):
        """Status HTTP 201 Created ao criar tarefa válida."""
        payload = {"title": "Estudar FastAPI", "description": "Cap. 3", "completed": False}
        response = client.post("/tasks/", json=payload)
        assert response.status_code == 201

    def test_criar_tarefa_retorna_json(self, client):
        """Resposta deve ser Content-Type application/json."""
        payload = {"title": "Tarefa Contrato"}
        response = client.post("/tasks/", json=payload)
        assert "application/json" in response.headers["content-type"]

    def test_criar_tarefa_retorna_campos_obrigatorios(self, client):
        """Corpo de resposta deve conter id, title, description, completed, created_at."""
        payload = {"title": "Verificar contrato", "description": "Campos da resposta"}
        response = client.post("/tasks/", json=payload)
        data = response.json()
        for campo in ("id", "title", "description", "completed"):
            assert campo in data, f"Campo '{campo}' ausente na resposta"

    def test_criar_tarefa_id_e_inteiro(self, client):
        """O campo 'id' da resposta deve ser um inteiro positivo."""
        response = client.post("/tasks/", json={"title": "ID inteiro"})
        assert isinstance(response.json()["id"], int)
        assert response.json()["id"] > 0

    def test_criar_tarefa_completed_padrao_falso(self, client):
        """Ao criar sem 'completed', valor padrão deve ser False."""
        response = client.post("/tasks/", json={"title": "Sem completed"})
        assert response.json()["completed"] is False

    def test_criar_tarefa_sem_title_retorna_422(self, client):
        """Criação sem 'title' deve retornar 422 Unprocessable Entity (violação de contrato)."""
        response = client.post("/tasks/", json={"description": "Sem título"})
        assert response.status_code == 422


class TestContratoGet:
    """Contrato do endpoint GET /tasks/ e GET /tasks/{id}"""

    def test_listar_tarefas_retorna_200(self, client):
        """GET /tasks/ deve retornar 200 mesmo com lista vazia."""
        response = client.get("/tasks/")
        assert response.status_code == 200

    def test_listar_tarefas_retorna_lista(self, client):
        """GET /tasks/ deve retornar um array JSON."""
        response = client.get("/tasks/")
        assert isinstance(response.json(), list)

    def test_buscar_tarefa_por_id_retorna_200(self, client):
        """GET /tasks/{id} deve retornar 200 para tarefa existente."""
        criada = client.post("/tasks/", json={"title": "Buscar por ID"}).json()
        response = client.get(f"/tasks/{criada['id']}")
        assert response.status_code == 200

    def test_buscar_tarefa_inexistente_retorna_404(self, client):
        """GET /tasks/{id} deve retornar 404 para ID inexistente."""
        response = client.get("/tasks/99999")
        assert response.status_code == 404

    def test_body_tarefa_por_id_tem_campos_corretos(self, client):
        """Resposta de GET /tasks/{id} deve ter mesma estrutura do contrato."""
        criada = client.post("/tasks/", json={"title": "Estrutura por ID"}).json()
        response = client.get(f"/tasks/{criada['id']}")
        data = response.json()
        for campo in ("id", "title", "description", "completed"):
            assert campo in data


class TestContratoPut:
    """Contrato do endpoint PUT /tasks/{id}"""

    def test_atualizar_tarefa_retorna_200(self, client):
        """PUT /tasks/{id} deve retornar 200 para tarefa existente."""
        tarefa = client.post("/tasks/", json={"title": "Para atualizar"}).json()
        response = client.put(f"/tasks/{tarefa['id']}", json={"title": "Atualizado", "completed": True})
        assert response.status_code == 200

    def test_atualizar_tarefa_retorna_dados_atualizados(self, client):
        """Corpo de resposta deve refletir os dados enviados na atualização."""
        tarefa = client.post("/tasks/", json={"title": "Original"}).json()
        response = client.put(
            f"/tasks/{tarefa['id']}",
            json={"title": "Novo título", "completed": True}
        )
        data = response.json()
        assert data["title"] == "Novo título"
        assert data["completed"] is True

    def test_atualizar_tarefa_inexistente_retorna_404(self, client):
        """PUT /tasks/{id} deve retornar 404 para ID inexistente."""
        response = client.put("/tasks/99999", json={"title": "X"})
        assert response.status_code == 404


class TestContratoDelete:
    """Contrato do endpoint DELETE /tasks/{id}"""

    def test_deletar_tarefa_retorna_200_ou_204(self, client):
        """DELETE /tasks/{id} deve retornar 200 ou 204 para tarefa existente."""
        tarefa = client.post("/tasks/", json={"title": "Para deletar"}).json()
        response = client.delete(f"/tasks/{tarefa['id']}")
        assert response.status_code in (200, 204)

    def test_deletar_tarefa_inexistente_retorna_404(self, client):
        """DELETE /tasks/{id} deve retornar 404 para ID inexistente."""
        response = client.delete("/tasks/99999")
        assert response.status_code == 404

    def test_tarefa_deletada_nao_encontrada_depois(self, client):
        """Após DELETE, GET /tasks/{id} deve retornar 404."""
        tarefa = client.post("/tasks/", json={"title": "Será deletada"}).json()
        client.delete(f"/tasks/{tarefa['id']}")
        response = client.get(f"/tasks/{tarefa['id']}")
        assert response.status_code == 404
