# Prompts de Testes de Integração — To-Do List API

Este diretório documenta os prompts utilizados com uma LLM (Large Language Model)
para gerar os casos de teste de integração disponíveis na pasta `tests/integration/`.

---

## Tipo 1 — Prompt de Contrato de API

**Arquivo gerado:** `tests/integration/test_api_contract.py`

**Objetivo:** Verificar que cada endpoint da API respeita o contrato REST definido
(status HTTP, estrutura do JSON de resposta, headers).

### Prompt Utilizado

```
Você é um especialista em testes de API REST. Dado o contrato a seguir de uma
API FastAPI de To-Do List com os endpoints:

- POST /tasks/       → Cria uma tarefa (201)
- GET /tasks/        → Lista tarefas com filtro opcional ?completed=bool e paginação ?skip=int&limit=int (200)
- GET /tasks/{id}    → Retorna tarefa por ID (200 / 404)
- PUT /tasks/{id}    → Atualiza tarefa por ID (200 / 404)
- DELETE /tasks/{id} → Deleta tarefa por ID (200 ou 204 / 404)

Schema de Task:
  id: int
  title: str (obrigatório)
  description: str | None
  completed: bool (padrão: False)
  created_at: datetime

Gere casos de teste de integração em Python com pytest e httpx que verifiquem:
1. Status HTTP correto para cada endpoint em cenário de sucesso
2. Estrutura do corpo de resposta JSON (campos obrigatórios e tipos)
3. Headers de resposta esperados (Content-Type: application/json)
4. Comportamento correto ao omitir o campo 'title' (deve retornar 422)

Use banco de dados SQLite em memória via fixture compartilhada conftest.py.
Organize os testes em classes por endpoint.
```

### Ajustes Necessários

- **Iteração 1 (prompt inicial):** A LLM gerou testes sem isolar o banco entre os testes,
  causando interferências entre casos. Ajuste: adicionar `scope="function"` na fixture.
- **Iteração 2:** Testes de DELETE não consideravam que a API poderia retornar 200 **ou** 204.
  Ajuste: usar `assert response.status_code in (200, 204)`.
- **Resultado final:** Testes bem estruturados, um por comportamento de contrato.

### Como esse tipo de prompt influenciou a qualidade

O prompt baseado em **contrato** produziu testes **precisos e atômicos** — cada teste
verifica exatamente uma propriedade do contrato (status, campo, tipo). Isso facilita a
identificação da causa raiz quando um teste falha. A diversidade foi menor (focada em
caminho feliz), mas a cobertura do contrato foi completa.

---

## Tipo 2 — Prompt de Cenários de Integração End-to-End

**Arquivo gerado:** `tests/integration/test_fluxo_completo.py`

**Objetivo:** Simular fluxos reais de uso do sistema, encadeando múltiplas chamadas HTTP.

### Prompt Utilizado

```
Você é um engenheiro de qualidade especializado em testes de integração.
Para uma API REST de To-Do List com FastAPI, crie casos de teste de integração
que simulem fluxos completos de uso real do sistema:

Fluxo 1 — CRUD Completo:
  Um usuário cria uma tarefa, lê pela listagem, busca pelo ID,
  atualiza o título e status, confirma via GET e por fim deleta.
  Verificar o estado do sistema após cada etapa.

Fluxo 2 — Filtro por Status:
  Criar tarefas com estados diferentes (pendente/concluída),
  usar GET /tasks/?completed=true e ?completed=false,
  verificar que apenas tarefas do status correto são retornadas.
  Incluir cenário onde o status é alterado via PUT e depois filtrado.

Fluxo 3 — Paginação:
  Criar 5+ tarefas, verificar limit=2, skip=3 e combinação skip+limit.
  Garantir que as páginas não se sobrepõem (IDs distintos).

Fluxo 4 — Consistência de Estado:
  Verificar que atualização parcial não corrompe outros campos.
  Verificar que listagem reflete corretamente deleções.

Use pytest com SQLite em memória. Cada cenário deve encadear chamadas
e verificar o estado intermediário do sistema.
```

### Ajustes Necessários

- **Iteração 1:** O prompt não especificava verificar estado **intermediário**; a LLM gerou
  testes que só checavam o resultado final. Ajuste: adicionar "verificar estado após cada etapa".
- **Iteração 2:** Faltavam assertions após o PUT para confirmar via GET. Ajuste: explicitar
  "confirme as alterações com uma nova chamada GET após o PUT".
- **Resultado final:** Testes ricos que cobrem fluxos reais e detectam problemas de estado.

### Como esse tipo de prompt influenciou a qualidade

O prompt baseado em **cenários** produziu testes com **maior diversidade e realismo**.
Os casos simulam como um usuário real interage com o sistema, capturando bugs de integração
entre endpoints que testes de contrato isolados não detectariam. A desvantagem é que
são mais difíceis de depurar quando falham.

---

## Tipo 3 — Prompt de Casos de Erro e Limites

**Arquivo gerado:** `tests/integration/test_casos_de_erro.py`

**Objetivo:** Cobrir robustez da API com entradas inválidas, valores extremos e operações indevidas.

### Prompt Utilizado

```
Você é um engenheiro de qualidade focado em testes negativos e casos de borda.
Para uma API FastAPI de To-Do List, gere casos de teste de integração que cubram:

Categoria 1 — Validação de Entrada:
  - 'title' ausente → 422
  - 'title' vazio ('') → 201 ou 422 (dependendo da implementação)
  - 'completed' com tipo errado (string) → 422
  - Payload completamente vazio → 422
  - Campos extras não reconhecidos → deve ser tolerado (não 500)

Categoria 2 — Recurso Não Encontrado:
  - GET/PUT/DELETE com ID inexistente → 404
  - Corpo do 404 deve conter 'detail'
  - ID negativo → 404 ou 422, nunca 500

Categoria 3 — Cascata de Erros:
  - Deletar duas vezes → segundo DELETE retorna 404
  - PUT após DELETE → 404
  - GET após DELETE → 404

Categoria 4 — Casos de Borda:
  - Title com 1000 caracteres → não deve causar 500
  - Description com 5000 caracteres → não deve causar 500
  - skip maior que total → lista vazia (não erro)
  - limit=0 → lista vazia
  - ID como string 'abc' → 422

Para cada caso, especifique o status HTTP esperado e se o corpo deve conter 'detail'.
Use pytest com SQLite em memória.
```

### Ajustes Necessários

- **Iteração 1:** A LLM assumiu que `title=""` sempre retornaria 422, o que depende da
  implementação. Ajuste: usar `assert status in (201, 422)` para não amarrar ao comportamento.
- **Iteração 2:** Testes de cascata não verificavam o **primeiro** DELETE antes do segundo.
  Ajuste: adicionar assertion do primeiro DELETE antes de testar o segundo.
- **Resultado final:** Testes defensivos que cobrem robustez sem depender de comportamentos não especificados.

### Como esse tipo de prompt influenciou a qualidade

O prompt de **casos de erro** produziu a maior **diversidade de cenários negativos**.
É o tipo mais útil para encontrar vulnerabilidades e comportamentos inesperados da API.
A LLM precisou de mais ajustes porque tende a assumir comportamentos específicos;
indicar `"pode ser X ou Y"` nas expectativas melhorou significativamente a qualidade.
