# mcp-salesdatabase

Servidor **MCP (Model Context Protocol)** em Python que conecta a uma base de
vendas em **PostgreSQL** e expõe **prompts**, **resources** e **tools** em
**português do Brasil** para análise de dados.

O dataset de referência é o
[Online Sales Dataset (Kaggle)](https://www.kaggle.com/datasets/shreyanshverma27/online-sales-dataset-popular-marketplace-data).
O schema (`docs/schema.sql`) cobre as tabelas `category`, `region`,
`payment_method`, `product` e `sales_order`.

## Pré-requisitos

- Python **3.14**
- [`uv`](https://docs.astral.sh/uv/) ≥ 0.4
- Acesso a um PostgreSQL com as tabelas de `docs/schema.sql` já populadas
- Opcional: Docker / Docker Compose / Kubernetes para empacotamento

## Configuração

Copie o template e ajuste as variáveis para apontar para o seu PostgreSQL:

```bash
cp .env.example .env
# edite .env com host/usuário/senha
```

Variáveis disponíveis (todas têm default):

| Variável            | Default     | Descrição                                  |
|---------------------|-------------|--------------------------------------------|
| `POSTGRES_HOST`     | `localhost` | Host do PostgreSQL                         |
| `POSTGRES_PORT`     | `5432`      | Porta                                      |
| `POSTGRES_DB`       | `salesdb`   | Nome do banco                              |
| `POSTGRES_USER`     | `salesuser` | Usuário                                    |
| `POSTGRES_PASSWORD` | (vazio)     | Senha                                      |
| `POSTGRES_POOL_MAX` | `5`         | Tamanho máximo do pool de conexões         |
| `MCP_TRANSPORT`     | `stdio`     | `stdio` (dev) ou `sse` (container)         |
| `MCP_SSE_HOST`      | `0.0.0.0`   | Host de bind no modo SSE                   |
| `MCP_SSE_PORT`      | `8000`      | Porta no modo SSE                          |

## Desenvolvimento (stdio + MCP Inspector)

```bash
uv sync
uv run mcp dev main.py
```

> O prompt original sugeria `uv run dev main.py`. O comando real do MCP CLI é
> **`uv run mcp dev main.py`**: ele inicia o Inspector e conecta ao servidor
> via stdio, permitindo testar as tools, prompts e resources visualmente.

Para rodar somente o servidor stdio (sem Inspector):

```bash
uv run python main.py
```

## Container (modo SSE)

```bash
docker compose up --build
```

O serviço sobe em `http://localhost:8000/sse`. Como o PostgreSQL é externo:

- Se ele rodar **na máquina host (fora do Docker)**, o `.env` pode usar
  `POSTGRES_HOST=host.docker.internal` (já há `extra_hosts` configurado no
  `docker-compose.yaml`).
- Se ele rodar **em outro container Docker**, conecte os dois à mesma network
  e use o nome do container como host.

Para testar o SSE diretamente:

```bash
curl -N http://localhost:8000/sse
```

## Kubernetes

Os manifestos ficam em `.container/`:

```bash
# 1. Crie o Secret com as credenciais do banco
kubectl create secret generic mcp-salesdatabase-db \
  --from-literal=POSTGRES_HOST=postgres.exemplo.svc.cluster.local \
  --from-literal=POSTGRES_PORT=5432 \
  --from-literal=POSTGRES_DB=salesdb \
  --from-literal=POSTGRES_USER=salesuser \
  --from-literal=POSTGRES_PASSWORD=sua-senha

# 2. Aplique deployment + service
kubectl apply -f .container/deployment.yaml
kubectl apply -f .container/service.yaml
```

O `Service` é `ClusterIP` na porta 8000. Exponha via Ingress / port-forward
conforme sua infraestrutura.

## Tools, Resources e Prompts

### Tools (PT-BR)

| Tool                          | Descrição                                                          |
|-------------------------------|--------------------------------------------------------------------|
| `executar_consulta_sql`       | Executa `SELECT`/`WITH` arbitrário (read-only, com LIMIT padrão)   |
| `listar_tabelas`              | Lista as tabelas do schema público                                  |
| `descrever_tabela`            | Colunas e tipos de uma tabela                                      |
| `vendas_por_categoria`        | Receita/unidades agrupadas por categoria                           |
| `vendas_por_regiao`           | Receita/unidades agrupadas por região                              |
| `vendas_por_metodo_pagamento` | Receita/unidades agrupadas por método de pagamento                 |
| `vendas_por_periodo`          | Receita por dia/mês/ano (`date_trunc`)                             |
| `top_produtos`                | Top N produtos por receita ou unidades                             |

> **Segurança**: a tool `executar_consulta_sql` só aceita queries que começam
> com `SELECT`/`WITH`. Comandos de escrita (`INSERT`, `UPDATE`, `DELETE`,
> `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `COPY` etc.) são bloqueados.

### Resources

| URI                                  | Conteúdo                                          |
|--------------------------------------|---------------------------------------------------|
| `salesdb://schema`                   | DDL completo (`docs/schema.sql`)                  |
| `salesdb://insights`                 | Descrição do dataset (`docs/data-sales.md`)       |
| `salesdb://tabelas`                  | Lista de tabelas + linhas estimadas (JSON)        |
| `salesdb://tabelas/{nome}/amostra`   | Até 20 linhas da tabela informada (JSON)          |

### Prompts

| Prompt                       | Objetivo                                                |
|------------------------------|---------------------------------------------------------|
| `analise_geral_vendas`       | Visão consolidada (categoria, região, top produtos)     |
| `tendencia_temporal`         | Sazonalidade e tendência (granularidade configurável)   |
| `comparativo_regional`       | Comparativo de regiões, opcionalmente por categoria     |
| `desempenho_produto`         | Top produtos por receita e por unidades                 |
| `analise_metodo_pagamento`   | Impacto dos métodos de pagamento na receita             |

## Estrutura do projeto

```
.
├── .container/                  Dockerfile + manifestos Kubernetes
├── docs/                        Schema, descrição do dataset e prompt inicial
├── server/
│   ├── app.py                   Instância FastMCP
│   ├── database.py              Pool psycopg + run_select read-only
│   ├── tools.py                 Tools MCP (PT-BR)
│   ├── resources.py             Resources MCP (PT-BR)
│   └── prompts.py               Prompts MCP (PT-BR)
├── docker-compose.yaml
├── main.py                      Entrypoint (stdio | sse)
└── pyproject.toml
```
