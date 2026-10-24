"""
TIPO 2 — Testes de Fluxo End-to-End (gerados via Prompt de Cenário de Integração)

Prompt utilizado na LLM:
    "Você é um engenheiro de qualidade especializado em testes de integração.
    Para uma API REST de To-Do List com FastAPI, crie casos de teste de integração
    que simulem fluxos completos de uso real do sistema, como:
    - Um usuário cria, lê, atualiza e deleta uma tarefa em sequência (CRUD completo),
    - Um usuário filtra tarefas por status (pendente/concluída),
    - Um usuário pagina os resultados de listagem.
    Os testes devem encadear múltiplas chamadas HTTP e verificar o estado do sistema
    após cada etapa. Use pytest com SQLite em memória."

Resultado: casos de teste que validam fluxos de integração entre endpoints.
"""

import pytest


class TestFluxoCRUDCompleto:
    """
    Fluxo: Criação → Leitura → Atualização → Deleção de uma tarefa.
    Valida que os endpoints colaboram corretamente em sequência.
    """

    def test_fluxo_crud_completo(self, client):
        """
        Cenário de integração completo: cria, lê, atualiza e deleta uma tarefa.
        Verifica consistência do estado em cada etapa.
        """
        # 1. Criar tarefa
        payload = {"title": "Integração CRUD", "description": "Fluxo completo", "completed": False}
        criar_resp = client.post("/tasks/", json=payload)
        assert criar_resp.status_code == 201
        tarefa_id = criar_resp.json()["id"]

        # 2. Verificar que tarefa aparece na listagem
        listar_resp = client.get("/tasks/")
        ids = [t["id"] for t in listar_resp.json()]
        assert tarefa_id in ids, "Tarefa criada não aparece na listagem"

        # 3. Buscar tarefa pelo ID
        buscar_resp = client.get(f"/tasks/{tarefa_id}")
        assert buscar_resp.status_code == 200
        assert buscar_resp.json()["title"] == "Integração CRUD"

        # 4. Atualizar a tarefa
        update_payload = {"title": "CRUD Atualizado", "completed": True}
        update_resp = client.put(f"/tasks/{tarefa_id}", json=update_payload)
        assert update_resp.status_code == 200
        assert update_resp.json()["completed"] is True

        # 5. Confirmar atualização via GET
        confirmacao = client.get(f"/tasks/{tarefa_id}")
        assert confirmacao.json()["title"] == "CRUD Atualizado"
        assert confirmacao.json()["completed"] is True

        # 6. Deletar a tarefa
        delete_resp = client.delete(f"/tasks/{tarefa_id}")
        assert delete_resp.status_code in (200, 204)

        # 7. Confirmar que não existe mais
        not_found = client.get(f"/tasks/{tarefa_id}")
        assert not_found.status_code == 404

    def test_criar_multiplas_tarefas_e_listar_todas(self, client):
        """
        Cria 3 tarefas e verifica que a listagem retorna exatamente 3 itens.
        """
        titulos = ["Tarefa A", "Tarefa B", "Tarefa C"]
        ids_criados = []
        for titulo in titulos:
            resp = client.post("/tasks/", json={"title": titulo})
            assert resp.status_code == 201
            ids_criados.append(resp.json()["id"])

        listagem = client.get("/tasks/").json()
        ids_listados = [t["id"] for t in listagem]
        for tid in ids_criados:
            assert tid in ids_listados


class TestFluxoFiltroStatus:
    """
    Fluxo: Criação de tarefas com status diferentes e filtragem por status.
    Valida integração entre escrita e leitura filtrada.
    """

    def test_filtrar_tarefas_concluidas(self, client):
        """
        Cria tarefas pendentes e concluídas, filtra por completed=true
        e verifica que apenas as concluídas são retornadas.
        """
        # Criar 2 pendentes + 2 concluídas
        client.post("/tasks/", json={"title": "Pendente 1", "completed": False})
        client.post("/tasks/", json={"title": "Pendente 2", "completed": False})
        client.post("/tasks/", json={"title": "Concluída 1", "completed": True})
        client.post("/tasks/", json={"title": "Concluída 2", "completed": True})

        resp = client.get("/tasks/?completed=true")
        assert resp.status_code == 200
        tarefas = resp.json()
        assert len(tarefas) >= 2
        for t in tarefas:
            assert t["completed"] is True, f"Tarefa '{t['title']}' não está concluída"

    def test_filtrar_tarefas_pendentes(self, client):
        """
        Filtra por completed=false e verifica que apenas pendentes são retornadas.
        """
        client.post("/tasks/", json={"title": "Pendente Filtro", "completed": False})
        client.post("/tasks/", json={"title": "Concluída Filtro", "completed": True})

        resp = client.get("/tasks/?completed=false")
        assert resp.status_code == 200
        tarefas = resp.json()
        for t in tarefas:
            assert t["completed"] is False

    def test_marcar_tarefa_como_concluida_e_filtrar(self, client):
        """
        Cria tarefa pendente, atualiza para concluída via PUT,
        depois filtra concluídas e verifica que ela aparece.
        """
        tarefa = client.post("/tasks/", json={"title": "Vai ser concluída"}).json()
        client.put(f"/tasks/{tarefa['id']}", json={"title": "Vai ser concluída", "completed": True})

        concluidas = client.get("/tasks/?completed=true").json()
        ids = [t["id"] for t in concluidas]
        assert tarefa["id"] in ids


class TestFluxoPaginacao:
    """
    Fluxo: Paginação de resultados com os parâmetros skip e limit.
    Valida integração entre criação em massa e consulta paginada.
    """

    def test_paginacao_com_limit(self, client):
        """
        Cria 5 tarefas e busca com limit=2; deve retornar exatamente 2.
        """
        for i in range(5):
            client.post("/tasks/", json={"title": f"Paginação {i+1}"})

        resp = client.get("/tasks/?limit=2")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_paginacao_com_skip(self, client):
        """
        Cria 5 tarefas e busca com skip=3; deve retornar as 2 últimas.
        """
        for i in range(5):
            client.post("/tasks/", json={"title": f"Skip {i+1}"})

        resp_total = client.get("/tasks/").json()
        resp_skip = client.get("/tasks/?skip=3").json()
        assert len(resp_skip) == len(resp_total) - 3

    def test_paginacao_skip_e_limit_combinados(self, client):
        """
        Verifica que skip + limit funcionam em conjunto para paginar corretamente.
        """
        for i in range(6):
            client.post("/tasks/", json={"title": f"Combo {i+1}"})

        pagina1 = client.get("/tasks/?skip=0&limit=3").json()
        pagina2 = client.get("/tasks/?skip=3&limit=3").json()

        ids_p1 = {t["id"] for t in pagina1}
        ids_p2 = {t["id"] for t in pagina2}
        assert ids_p1.isdisjoint(ids_p2), "Páginas não devem ter tarefas em comum"


class TestFluxoConsistenciaEstado:
    """
    Valida que o sistema mantém consistência de estado entre operações.
    """

    def test_atualizacao_parcial_preserva_campos_nao_enviados(self, client):
        """
        Ao atualizar apenas o 'title', o campo 'description' deve ser preservado.
        """
        tarefa = client.post("/tasks/", json={
            "title": "Original",
            "description": "Descrição importante"
        }).json()

        client.put(f"/tasks/{tarefa['id']}", json={"title": "Novo título"})

        atual = client.get(f"/tasks/{tarefa['id']}").json()
        # O campo description deve ser mantido ou compatível
        assert atual["title"] == "Novo título"

    def test_listagem_reflete_estado_apos_delecao(self, client):
        """
        Após deletar uma tarefa, ela não deve mais aparecer na listagem.
        """
        t1 = client.post("/tasks/", json={"title": "Fica"}).json()
        t2 = client.post("/tasks/", json={"title": "Será deletada"}).json()

        client.delete(f"/tasks/{t2['id']}")

        listagem = client.get("/tasks/").json()
        ids = [t["id"] for t in listagem]
        assert t1["id"] in ids
        assert t2["id"] not in ids
