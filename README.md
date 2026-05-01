# To-Do List (MVP)

Uma API RESTful para gerenciamento de tarefas (To-Do List), desenvolvida com Python, FastAPI e SQLite. O projeto tem como foco principal aplicar boas práticas de engenharia de software e manter uma estrutura limpa e profissional.

---

## 📑 Sumário
- [Stack Tecnológico](#stack-tecnológico)
- [Funcionalidades](#funcionalidades)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Pré-requisitos e Execução](#pré-requisitos-e-execução)
- [Documentação da API (Endpoints)](#documentação-da-api-endpoints)
- [Testes e Linter](#testes-e-linter)
- [Códigos de Status HTTP](#códigos-de-status-http)

---

## 🛠️ Stack Tecnológico
| Camada | Tecnologia |
|---|---|
| **Framework** | [FastAPI](https://fastapi.tiangolo.com/) |
| **Linguagem** | Python 3.8+ |
| **Validação** | Pydantic |
| **Servidor** | Uvicorn |
| **Persistência** | SQLite (In-memory via SQLAlchemy para testes) |
| **Testes** | Pytest |
| **Linter** | Flake8 |

---

## 🚀 Funcionalidades
- **CRUD Completo de Tarefas**: Criar, Ler, Atualizar e Deletar tarefas.
- **Filtros**: Recuperar tarefas apenas concluídas ou pendentes.
- **Estatísticas**: Dashboard básico retornando o quantitativo total, pendente e concluído de tarefas.
- **Segurança e Validação**: Proteção de injeção e validação de tipos usando schemas do Pydantic.

---

## 💻 Estrutura do Projeto

```text
esp-ti-es-todolist-api/
├── app/
│   ├── main.py          # Ponto de entrada (entry point) e rotas principais
│   ├── crud.py          # Lógica de acesso a dados e regras de negócio
│   ├── models.py        # Mapeamento Objeto-Relacional (SQLAlchemy)
│   ├── schemas.py       # Validações de request/response (Pydantic)
│   └── database.py      # Configuração de conexão com o banco
├── tests/
│   └── test_main.py     # Suite de testes isolados rodando em SQLite :memory:
├── Makefile             # Atalhos de terminal (make run, make test, make lint)
├── .env.example         # Exemplo das variáveis de ambiente base
├── .flake8              # Regras de formatação (PEP-8)
├── requirements.txt     # Dependências para pip
└── README.md            # Documentação central do repositório
```

---

## ⚙️ Pré-requisitos e Execução

### Passo a passo para rodar localmente:
1. **Clone o repositório:**
   ```bash
   git clone <sua-url>
   cd esp-ti-es-todolist-api
   ```
2. **Crie um ambiente virtual (venv):**
   ```bash
   python -m venv venv
   # No Windows
   venv\Scripts\activate
   # No Linux/Mac
   source venv/bin/activate
   ```
3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configuração inicial (opcional):**
   Copie o modelo de ambiente usando `cp .env.example .env`.
5. **Inicie a aplicação:**
   Você pode usar o atalho do Makefile (`make run`) ou digitar:
   ```bash
   uvicorn app.main:app --reload
   ```

Acesse a **Documentação Interativa Swagger** gerada automaticamente em:
[http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🌐 Documentação da API (Endpoints)

Base URL Padrão: `http://localhost:8000/tasks`

### 1. Obter Estatísticas (Dashboard)
Retorna a contagem de tarefas.
```http
GET /tasks/stats
```
**Exemplo `curl`:**
```bash
curl http://localhost:8000/tasks/stats
```
**Resposta (200 OK):**
```json
{
  "total": 5,
  "pending": 3,
  "completed": 2
}
```

### 2. Criar uma Nova Tarefa
```http
POST /tasks/
```
**Body (JSON):**
```json
{
  "title": "Aprender FastAPI",
  "description": "Finalizar módulo de CRUD com SQLite"
}
```
**Exemplo `curl`:**
```bash
curl -X POST http://localhost:8000/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Aprender FastAPI", "description": "Finalizar módulo de CRUD com SQLite"}'
```

### 3. Listar as Tarefas
Permite paginação e filtro.
```http
GET /tasks/?skip=0&limit=100&completed=false
```
**Exemplo `curl`:**
```bash
curl "http://localhost:8000/tasks/?completed=false"
```

### 4. Obter Tarefa por ID
```http
GET /tasks/{task_id}
```

### 5. Atualizar Tarefa
Permite atualizações parciais ou totais.
```http
PUT /tasks/{task_id}
```
**Body (JSON):**
```json
{
  "completed": true
}
```

### 6. Deletar Tarefa
```http
DELETE /tasks/{task_id}
```

---

## 📊 Códigos de Status HTTP
A API utiliza as convenções restritas de código:
| Código | Significado | Exemplo de uso na aplicação |
|---|---|---|
| `200 OK` | Sucesso | Retorno do GET ou de atualizações. |
| `201 Created` | Criado | Retorno exclusivo após criação no POST. |
| `204 No Content` | Sem conteúdo | Retorno após DELETE bem sucedido. |
| `404 Not Found` | Não encontrado | Quando o ID da tarefa solicitada não existe no banco. |
| `422 Unprocessable`| Erro de Validação | Quando um campo obrigatório está faltando (ex: `title`). |

---

## 🧪 Testes e Linter

- **Rodar os testes unitários:**
  ```bash
  make test
  ```
  *(Ou diretamente: `pytest -v`)*
  
- **Verificar os padrões do código com Flake8:**
  ```bash
  make lint
  ```
  *(Ou diretamente: `flake8 app/ tests/`)*

---

Este projeto é desenvolvido com um histórico focado em padronização *Conventional Commits* para demonstração de versionamento saudável.
