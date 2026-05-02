"""Resources MCP que expõem schema, insights e amostras de dados. Em PT-BR."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .app import mcp
from .database import run_select

_DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"


def _ler_doc(arquivo: str) -> str:
    caminho = _DOCS_DIR / arquivo
    if not caminho.exists():
        return f"(arquivo {arquivo} não encontrado em docs/)"
    return caminho.read_text(encoding="utf-8")


@mcp.resource(
    uri="salesdb://schema",
    name="Schema da base de vendas",
    description=(
        "DDL completo (CREATE TABLE) da base de vendas. Útil para entender "
        "tabelas, colunas e relacionamentos antes de escrever consultas."
    ),
    mime_type="text/plain",
)
def schema_sql() -> str:
    """Retorna o conteúdo de docs/schema.sql."""
    return _ler_doc("schema.sql")


@mcp.resource(
    uri="salesdb://insights",
    name="Insights e descrição do dataset",
    description=(
        "Descrição em alto nível do dataset de vendas, colunas e perguntas "
        "analíticas sugeridas."
    ),
    mime_type="text/markdown",
)
def insights_dataset() -> str:
    """Retorna o conteúdo de docs/data-sales.md."""
    return _ler_doc("data-sales.md")


@mcp.resource(
    uri="salesdb://tabelas",
    name="Tabelas disponíveis",
    description=(
        "Lista todas as tabelas do schema público com a contagem aproximada "
        "de linhas. Em formato JSON."
    ),
    mime_type="application/json",
)
def listar_tabelas_resource() -> str:
    """JSON com a lista de tabelas e linhas estimadas."""
    sql = """
        SELECT
            t.table_name AS tabela,
            COALESCE(c.reltuples::bigint, 0) AS linhas_estimadas
        FROM information_schema.tables t
        LEFT JOIN pg_class c ON c.relname = t.table_name
        WHERE t.table_schema = 'public'
          AND t.table_type = 'BASE TABLE'
        ORDER BY t.table_name
    """
    rows = run_select(sql)
    return json.dumps(rows, ensure_ascii=False, indent=2, default=str)


@mcp.resource(
    uri="salesdb://tabelas/{nome}/amostra",
    name="Amostra de linhas de uma tabela",
    description=(
        "Retorna até 20 linhas da tabela informada, em JSON. Útil para "
        "inspecionar rapidamente o conteúdo de uma tabela antes de escrever "
        "uma consulta mais elaborada."
    ),
    mime_type="application/json",
)
def amostra_tabela(nome: str) -> str:
    """Retorna até 20 linhas da tabela. Valida o nome antes de interpolar."""
    if not nome.replace("_", "").isalnum():
        raise ValueError("Nome de tabela inválido.")

    existe = run_select(
        """
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = %s
        """,
        (nome,),
    )
    if not existe:
        raise ValueError(f"Tabela '{nome}' não encontrada no schema público.")

    rows: list[dict[str, Any]] = run_select(
        f"SELECT * FROM {nome} LIMIT 20",
        apply_default_limit=False,
    )
    return json.dumps(rows, ensure_ascii=False, indent=2, default=str)
