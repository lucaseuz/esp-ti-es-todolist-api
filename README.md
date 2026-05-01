# To-Do List (MVP)

Uma API RESTful minimalista de To-Do List construída com **Python**, **FastAPI**, **SQLAlchemy** e **SQLite**.

Este projeto demonstra fundamentos de engenharia de software, incluindo organização modular, validações de dados via Pydantic e testes automatizados.

## 🚀 Funcionalidades
- **Criar Tarefa:** Adiciona uma nova tarefa com título (obrigatório) e descrição.
- **Listar Tarefas:** Recupera todas as tarefas, com paginação (`skip`, `limit`) e filtro opcional por `completed` (pendente/concluída).
- **Ler Tarefa Única:** Retorna detalhes de uma tarefa específica pelo ID.
- **Atualizar Tarefa:** Permite modificar o título, a descrição e o status de conclusão de uma tarefa.
- **Deletar Tarefa:** Exclui uma tarefa do banco de dados.

---

## 🛠️ Tecnologias Utilizadas
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web rápido para construção de APIs.
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM para interação com o banco de dados.
- [SQLite](https://www.sqlite.org/) - Banco de dados local leve.
- [Pydantic](https://docs.pydantic.dev/) - Validação de dados.
- [Pytest](https://docs.pytest.org/) - Framework de testes automatizados.

---

## 💻 Estrutura do Projeto

```
esp-ti-es-todolist-api/
├── app/
│   ├── main.py          # Ponto de entrada e rotas (endpoints)
│   ├── crud.py          # Operações de banco de dados (Create, Read, Update, Delete)
│   ├── models.py        # Modelos das tabelas do banco de dados
│   ├── schemas.py       # Validações de entrada/saída (Pydantic)
│   └── database.py      # Configuração da conexão com SQLite
├── tests/
│   └── test_main.py     # Suite de testes automatizados
├── requirements.txt     # Dependências do projeto
├── .gitignore           # Arquivos e pastas a serem ignorados pelo git
└── README.md            # Esta documentação
```

---

## ⚙️ Como Instalar e Rodar

1. **Clone o repositório:**
   ```bash
   git clone <url-do-repositorio>
   cd esp-ti-es-todolist-api
   ```

2. **Crie um ambiente virtual (opcional, mas recomendado):**
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

4. **Inicie o servidor localmente:**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Acesse a Documentação Interativa:**
   O FastAPI gera documentação automática. Abra o navegador e acesse:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Como rodar os Testes

Com as dependências instaladas e o ambiente virtual ativado, rode o comando:
```bash
pytest
```
Os testes utilizam um banco de dados em memória, garantindo isolamento total e rapidez.

---

## 📝 Regras de Contribuição e Commits

Este repositório segue os padrões de [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
Exemplos utilizados no desenvolvimento:
- `init: setup inicial do projeto com dependências e .gitignore`
- `feat(db): configuração do banco de dados SQLite e modelos do SQLAlchemy`
- `feat(api): implementação dos schemas Pydantic e rotas do CRUD de tarefas`
- `test: adição da suíte de testes automatizados com Pytest`
- `docs: criação do README.md completo com instruções de uso`
- `chore: formatação de código e preparação para a release inicial`
