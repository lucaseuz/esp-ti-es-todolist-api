# Testes de Integração — To-Do List API

Este diretório contém os **casos de teste de integração** gerados com auxílio de LLM
(Large Language Model), como parte da atividade do fórum da Unidade III da pós-graduação.

## Cenário de Integração

A API To-Do List é construída com **FastAPI + SQLAlchemy + SQLite** e expõe um conjunto
de endpoints REST para gerenciamento de tarefas. O cenário de integração testado é a
**comunicação entre o cliente (TestClient) e a camada de serviço REST**, passando pela
validação de dados (Pydantic/schemas), lógica de negócio (CRUD) e persistência (SQLAlchemy).

```
[Cliente HTTP] ──→ [FastAPI Router] ──→ [CRUD/Serviço] ──→ [SQLAlchemy ORM] ──→ [SQLite]
```

## Estrutura dos Arquivos

```
tests/
├── integration/
│   ├── conftest.py              # Fixture compartilhada: banco SQLite em memória
│   ├── test_api_contract.py     # Tipo 1: Testes de Contrato de API
│   ├── test_fluxo_completo.py   # Tipo 2: Testes de Fluxo End-to-End
│   └── test_casos_de_erro.py    # Tipo 3: Testes de Casos de Erro e Limites
└── prompts/
    └── PROMPTS.md               # Documentação completa dos prompts utilizados
```

## Tipos de Prompt Utilizados

### 🔷 Tipo 1 — Prompt de Contrato de API (`test_api_contract.py`)

Focado em verificar que cada endpoint respeita o **contrato REST** definido:
status HTTP correto, estrutura do JSON de resposta e headers esperados.

**Influência na qualidade:** gerou testes atômicos e precisos, ideais para detectar
regressões de contrato. Menor diversidade de cenários, porém alta confiabilidade.

### 🔶 Tipo 2 — Prompt de Cenários End-to-End (`test_fluxo_completo.py`)

Focado em simular **fluxos reais de uso**: CRUD completo, filtros, paginação
e consistência de estado entre operações encadeadas.

**Influência na qualidade:** maior diversidade e realismo. Detecta bugs de integração
entre endpoints que testes isolados não encontrariam.

### 🔴 Tipo 3 — Prompt de Casos de Erro (`test_casos_de_erro.py`)

Focado em **robustez**: entradas inválidas, recursos inexistentes, operações em cascata
e valores extremos.

**Influência na qualidade:** maior cobertura de cenários negativos. Requer mais ajustes
de prompt para evitar suposições muito específicas da LLM sobre o comportamento da API.

## Ajustes de Prompt Necessários

| Tipo de Prompt | Problema Inicial | Ajuste Aplicado |
|----------------|-----------------|-----------------|
| Contrato | Banco não isolado entre testes | Especificar `scope="function"` na fixture |
| Contrato | DELETE esperava só 200 | Indicar que pode ser 200 **ou** 204 |
| Fluxo E2E | Não verificava estado intermediário | Adicionar "verificar estado após cada etapa" |
| Fluxo E2E | Faltava GET após PUT | Explicitar "confirme com nova chamada GET" |
| Casos de Erro | Assumia `title=""` → 422 fixo | Usar `assert status in (201, 422)` |
| Casos de Erro | Cascata sem checar 1º DELETE | Adicionar assertion do primeiro DELETE |

## Como Executar

```bash
# Instalar dependências
pip install fastapi uvicorn sqlalchemy pytest httpx

# Executar todos os testes de integração
pytest tests/integration/ -v

# Executar apenas os de contrato
pytest tests/integration/test_api_contract.py -v

# Executar com relatório de cobertura
pytest tests/integration/ -v --tb=short
```

## Reflexão: GenAI como Copiloto

A GenAI funcionou como um excelente **copiloto** na construção da suíte de integração:

- **Acelerou a criação** de casos de teste que levariam horas para escrever manualmente
- **Aumentou a diversidade** de cenários, especialmente negativos que tendemos a esquecer
- **Requer revisão humana**: a LLM faz suposições que podem não corresponder à implementação real
- **Prompts mais específicos = resultados melhores**: incluir exemplos de payloads, status codes
  esperados e organização desejada reduziu significativamente o retrabalho
- O melhor uso é **iterativo**: gerar → revisar → refinar o prompt → gerar novamente
