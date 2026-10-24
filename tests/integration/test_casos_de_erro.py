"""
TIPO 3 — Testes de Casos de Erro e Limites (gerados via Prompt de Casos de Erro)

Prompt utilizado na LLM:
    "Você é um engenheiro de qualidade focado em testes negativos e casos de borda.
    Para uma API FastAPI de To-Do List, gere casos de teste de integração que cubram:
    - Entradas inválidas (tipo errado, campo obrigatório ausente, string vazia),
    - IDs que não existem (404),
    - Payloads com campos extras (deve ser tolerado),
    - Valores extremos (strings muito longas, números negativos como ID),
    - Operações em cascata (tentar usar recurso deletado).
    Registre o status HTTP e o corpo do erro esperado. Use pytest com SQLite em memória."

Resultado: casos de teste que cobrem robustez e tratamento de erros da API.
"""

import pytest


class TestErrosValidacao:
    """Testa respostas a payloads inválidos — validação de entrada."""

    def test_criar_sem_title_retorna_422(self, client):
        """Campo 'title' é obrigatório; ausência deve resultar em 422."""
        response = client.post("/tasks/", json={"description": "Sem título"})
        assert response.status_code == 422

    def test_criar_com_title_vazio_deve_ser_tratado(self, client):
        """
        Title vazio ('') pode ser aceito (200/201) ou rejeitado (422).
        O importante é que a API retorne uma resposta definida, sem erro 500.
        """
        response = client.post("/tasks/", json={"title": ""})
        assert response.status_code in (201, 422), (
            f"Esperado 201 ou 422, obtido {response.status_code}"
        )

    def test_criar_com_completed_tipo_errado_retorna_422(self, client):
        """'completed' deve ser booleano; enviar string inválida deve retornar 422."""
        response = client.post("/tasks/", json={"title": "Erro tipo", "completed": "nao_e_bool"})
        assert response.status_code == 422

    def test_criar_com_payload_vazio_retorna_422(self, client):
        """Payload completamente vazio deve retornar 422."""
        response = client.post("/tasks/", json={})
        assert response.status_code == 422

    def test_criar_com_campos_extras_deve_ser_tolerado(self, client):
        """
        Campos extras não reconhecidos pelo schema devem ser ignorados.
        A API não deve retornar 500.
        """
        payload = {
            "title": "Com campo extra",
            "campo_inexistente": "valor qualquer",
            "outro_campo": 12345,
        }
        response = client.post("/tasks/", json=payload)
        assert response.status_code in (201, 422), (
            f"Não deveria retornar 500. Status: {response.status_code}"
        )


class TestErrosRecursoNaoEncontrado:
    """Testa respostas quando o recurso não existe."""

    def test_buscar_id_inexistente_retorna_404(self, client):
        """GET /tasks/99999 deve retornar 404."""
        response = client.get("/tasks/99999")
        assert response.status_code == 404

    def test_atualizar_id_inexistente_retorna_404(self, client):
        """PUT /tasks/99999 deve retornar 404."""
        response = client.put("/tasks/99999", json={"title": "Não existe"})
        assert response.status_code == 404

    def test_deletar_id_inexistente_retorna_404(self, client):
        """DELETE /tasks/99999 deve retornar 404."""
        response = client.delete("/tasks/99999")
        assert response.status_code == 404

    def test_404_tem_corpo_json_com_detail(self, client):
        """Resposta 404 deve conter corpo JSON com chave 'detail'."""
        response = client.get("/tasks/99999")
        data = response.json()
        assert "detail" in data, "Resposta 404 deve conter 'detail' no corpo"

    def test_buscar_id_negativo_retorna_404_ou_422(self, client):
        """ID negativo não existe; deve retornar 404 ou 422, nunca 500."""
        response = client.get("/tasks/-1")
        assert response.status_code in (404, 422), (
            f"ID negativo não deve causar 500. Status: {response.status_code}"
        )


class TestErrosCascata:
    """Testa operações em recursos já deletados (cascata de erros)."""

    def test_deletar_tarefa_duas_vezes_segundo_retorna_404(self, client):
        """
        Deletar a mesma tarefa duas vezes: segundo DELETE deve retornar 404.
        """
        tarefa = client.post("/tasks/", json={"title": "Deletar duas vezes"}).json()
        primeiro = client.delete(f"/tasks/{tarefa['id']}")
        assert primeiro.status_code in (200, 204)

        segundo = client.delete(f"/tasks/{tarefa['id']}")
        assert segundo.status_code == 404

    def test_atualizar_tarefa_apos_delecao_retorna_404(self, client):
        """
        Tentar atualizar uma tarefa deletada deve retornar 404.
        """
        tarefa = client.post("/tasks/", json={"title": "Será deletada"}).json()
        client.delete(f"/tasks/{tarefa['id']}")

        response = client.put(f"/tasks/{tarefa['id']}", json={"title": "Após deleção"})
        assert response.status_code == 404

    def test_buscar_tarefa_apos_delecao_retorna_404(self, client):
        """
        Buscar tarefa após deleção deve retornar 404.
        """
        tarefa = client.post("/tasks/", json={"title": "Buscar deletada"}).json()
        client.delete(f"/tasks/{tarefa['id']}")

        response = client.get(f"/tasks/{tarefa['id']}")
        assert response.status_code == 404


class TestCasosDeBorda:
    """Testa valores extremos e casos de borda."""

    def test_title_muito_longo_nao_causa_erro_500(self, client):
        """
        Title com 1000 caracteres não deve causar erro interno (500).
        Pode ser aceito (201) ou rejeitado por validação (422).
        """
        titulo_longo = "A" * 1000
        response = client.post("/tasks/", json={"title": titulo_longo})
        assert response.status_code in (201, 422), (
            f"Título longo não deve causar 500. Status: {response.status_code}"
        )

    def test_description_muito_longa_nao_causa_500(self, client):
        """Description com 5000 caracteres não deve causar erro 500."""
        desc_longa = "B" * 5000
        response = client.post("/tasks/", json={"title": "OK", "description": desc_longa})
        assert response.status_code in (201, 422)

    def test_paginacao_skip_maior_que_total_retorna_lista_vazia(self, client):
        """
        Paginação com skip maior que o total de registros deve retornar lista vazia.
        """
        client.post("/tasks/", json={"title": "Só uma tarefa"})
        response = client.get("/tasks/?skip=1000")
        assert response.status_code == 200
        assert response.json() == []

    def test_limit_zero_retorna_lista_vazia(self, client):
        """limit=0 deve retornar lista vazia, não erro."""
        client.post("/tasks/", json={"title": "Qualquer tarefa"})
        response = client.get("/tasks/?limit=0")
        assert response.status_code == 200
        assert response.json() == []

    def test_id_como_string_retorna_422(self, client):
        """GET /tasks/abc deve retornar 422 (ID deve ser inteiro)."""
        response = client.get("/tasks/abc")
        assert response.status_code == 422
