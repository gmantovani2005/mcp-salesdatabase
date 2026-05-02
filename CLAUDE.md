# CLAUDE.md

Este arquivo orienta o Claude Code (claude.ai/code) ao trabalhar neste
repositório.

## Visão geral

`mcp-salesdatabase` é um servidor **MCP (Model Context Protocol)** em Python
que conecta a um PostgreSQL contendo dados de vendas online (categorias,
regiões, produtos, métodos de pagamento, pedidos) e expõe **prompts**,
**resources** e **tools** em **português do Brasil** para análises de
vendas.

- Em desenvolvimento, roda em `stdio` e é inspecionado com o MCP Inspector.
- Em container/Kubernetes, roda em `sse` na porta 8000.
- O PostgreSQL é **externo** (não é provisionado pelo projeto). Schema de
  referência em `docs/schema.sql`.

## Stack

- Python **3.14** (ver `.python-version`)
- [`uv`](https://docs.astral.sh/uv/) para dependências e execução
- `mcp[cli]` (MCP Python SDK + Inspector)
- `psycopg[binary,pool]` v3 (PostgreSQL com pool nativo)
- `python-dotenv` (carrega `.env` em dev)

## Comandos comuns

```bash
# Sincronizar dependências
uv sync

# Dev (stdio + MCP Inspector)
uv run mcp dev main.py

# Dev (stdio puro, sem Inspector)
uv run python main.py

# SSE local (sem Docker)
MCP_TRANSPORT=sse uv run python main.py

# Container (SSE em :8000)
docker compose up --build

# Kubernetes
kubectl apply -f .container/deployment.yaml
kubectl apply -f .container/service.yaml
```

## Estrutura

```
.
├── .container/             Dockerfile + manifestos K8s (deployment, service)
├── docs/                   Schema (schema.sql) e descrição do dataset
├── server/
│   ├── app.py              FastMCP singleton
│   ├── database.py         Pool psycopg + helper run_select() read-only
│   ├── tools.py            @mcp.tool — PT-BR
│   ├── resources.py        @mcp.resource — PT-BR
│   └── prompts.py          @mcp.prompt — PT-BR
├── main.py                 Entrypoint (stdio|sse via MCP_TRANSPORT)
├── docker-compose.yaml
└── pyproject.toml
```

## Convenções

- **Idioma**: descrições de tools/resources/prompts e textos dos prompts
  ficam **em português do Brasil**, alinhando com prompts dos usuários.
- **Read-only**: a base é tratada como somente leitura. Toda execução SQL
  passa por `server.database.run_select`, que valida que a query começa com
  `SELECT`/`WITH` e bloqueia comandos de escrita.
- **Parametrização**: nunca interpolar valores de usuário em SQL. Sempre
  usar parâmetros (`%s`).
- **LIMIT default**: queries sem `LIMIT` recebem `LIMIT 1000` automaticamente
  para proteger o banco e o transporte.
- **Configuração**: variáveis em `.env` (carregadas por `python-dotenv` em
  dev). Em container/k8s, vêm via env/Secret.

## Como adicionar uma nova tool/resource/prompt

1. Crie a função no módulo correspondente (`server/tools.py`,
   `server/resources.py` ou `server/prompts.py`).
2. Decore com `@mcp.tool(...)`, `@mcp.resource(...)` ou `@mcp.prompt(...)`,
   com `name` e `description` em **PT-BR**.
3. Use `run_select` para qualquer acesso ao banco.
4. Não é necessário registrar manualmente: `server/app.py` importa os três
   módulos no momento de criar o `FastMCP` (efeito colateral dos
   decoradores).

## Variáveis de ambiente

Ver `.env.example` para a lista completa. Resumo:

- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`,
  `POSTGRES_PASSWORD`, `POSTGRES_POOL_MAX`
- `MCP_TRANSPORT` (`stdio` | `sse`), `MCP_SSE_HOST`, `MCP_SSE_PORT`
