# mcp-salesdatabase

An **MCP (Model Context Protocol)** server in Python that connects to a sales
database in **PostgreSQL** and exposes **prompts**, **resources**, and **tools** in
**Brazilian Portuguese** for data analysis.

The reference dataset is the
[Online Sales Dataset (Kaggle)](https://www.kaggle.com/datasets/shreyanshverma27/online-sales-dataset-popular-marketplace-data).
The schema (`docs/schema.sql`) covers the `category`, `region`,
`payment_method`, `product`, and `sales_order` tables.

## Prerequisites

- Python **3.14**
- [`uv`](https://docs.astral.sh/uv/) ≥ 0.4
- Access to a PostgreSQL database with the tables from `docs/schema.sql` already populated
- Optional: Docker / Docker Compose / Kubernetes for packaging

## Configuration

Copy the template and adjust the variables to point to your PostgreSQL:

```bash
cp .env.example .env
# edit .env with host/user/password
```

Available variables (all have defaults):

| Variable            | Default     | Description                                |
|---------------------|-------------|--------------------------------------------|
| `POSTGRES_HOST`     | `localhost` | PostgreSQL host                            |
| `POSTGRES_PORT`     | `5432`      | Port                                       |
| `POSTGRES_DB`       | `salesdb`   | Database name                              |
| `POSTGRES_USER`     | `salesuser` | User                                       |
| `POSTGRES_PASSWORD` | (empty)     | Password                                   |
| `POSTGRES_POOL_MAX` | `5`         | Maximum connection pool size               |
| `MCP_TRANSPORT`     | `stdio`     | `stdio` (dev) or `sse` (container)         |
| `MCP_SSE_HOST`      | `0.0.0.0`   | Bind host in SSE mode                      |
| `MCP_SSE_PORT`      | `8000`      | Port in SSE mode                           |

## Development (stdio + MCP Inspector)

```bash
uv sync
uv run mcp dev main.py
```

> The original prompt suggested `uv run dev main.py`. The actual MCP CLI command is
> **`uv run mcp dev main.py`**: it starts the Inspector and connects to the server
> via stdio, allowing you to test tools, prompts, and resources visually.

To run only the stdio server (without Inspector):

```bash
uv run python main.py
```

## Container (SSE mode)

```bash
docker compose up --build
```

The service will be up at `http://localhost:8000/sse`. Since PostgreSQL is external:

- If it runs **on the host machine (outside Docker)**, `.env` can use
  `POSTGRES_HOST=host.docker.internal` (`extra_hosts` is already configured in
  `docker-compose.yaml`).
- If it runs **in another Docker container**, connect both to the same network
  and use the container name as the host.

To test SSE directly:

```bash
curl -N http://localhost:8000/sse
```

## Kubernetes

Manifests are located in `.container/`:

```bash
# 1. Create the Secret with database credentials
kubectl create secret generic mcp-salesdatabase-db \
  --from-literal=POSTGRES_HOST=postgres.example.svc.cluster.local \
  --from-literal=POSTGRES_PORT=5432 \
  --from-literal=POSTGRES_DB=salesdb \
  --from-literal=POSTGRES_USER=salesuser \
  --from-literal=POSTGRES_PASSWORD=your-password

# 2. Apply deployment + service
kubectl apply -f .container/deployment.yaml
kubectl apply -f .container/service.yaml
```

The `Service` is `ClusterIP` on port 8000. Expose it via Ingress / port-forward
according to your infrastructure.

## Tools, Resources, and Prompts

### Tools (PT-BR)

| Tool                          | Description                                                        |
|-------------------------------|--------------------------------------------------------------------|
| `executar_consulta_sql`       | Executes arbitrary `SELECT`/`WITH` (read-only, with default LIMIT) |
| `listar_tabelas`              | Lists tables in the public schema                                  |
| `descrever_tabela`            | Columns and types of a table                                       |
| `vendas_por_categoria`        | Revenue/units grouped by category                                  |
| `vendas_por_regiao`           | Revenue/units grouped by region                                    |
| `vendas_por_metodo_pagamento` | Revenue/units grouped by payment method                            |
| `vendas_por_periodo`          | Revenue by day/month/year (`date_trunc`)                           |
| `top_produtos`                | Top N products by revenue or units                                 |

> **Security**: the `executar_consulta_sql` tool only accepts queries starting
> with `SELECT`/`WITH`. Write commands (`INSERT`, `UPDATE`, `DELETE`,
> `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `COPY`, etc.) are blocked.

### Resources

| URI                                  | Content                                           |
|--------------------------------------|---------------------------------------------------|
| `salesdb://schema`                   | Complete DDL (`docs/schema.sql`)                  |
| `salesdb://insights`                 | Dataset description (`docs/data-sales.md`)        |
| `salesdb://tabelas`                  | List of tables + estimated rows (JSON)            |
| `salesdb://tabelas/{nome}/amostra`   | Up to 20 rows from the specified table (JSON)     |

### Prompts

| Prompt                       | Objective                                               |
|------------------------------|---------------------------------------------------------|
| `analise_geral_vendas`       | Consolidated view (category, region, top products)      |
| `tendencia_temporal`         | Seasonality and trends (configurable granularity)       |
| `comparativo_regional`       | Region comparison, optionally by category               |
| `desempenho_produto`         | Top products by revenue and units                       |
| `analise_metodo_pagamento`   | Impact of payment methods on revenue                    |

## Project structure

```
.
├── .container/                  Dockerfile + Kubernetes manifests
├── docs/                        Schema, dataset description, and initial prompt
├── server/
│   ├── app.py                   FastMCP instance
│   ├── database.py              psycopg pool + read-only run_select
│   ├── tools.py                 MCP Tools (PT-BR)
│   ├── resources.py             MCP Resources (PT-BR)
│   └── prompts.py               MCP Prompts (PT-BR)
├── docker-compose.yaml
├── main.py                      Entrypoint (stdio | sse)
└── pyproject.toml
```
