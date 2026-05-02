"""Tools MCP para análise de vendas. Descrições em PT-BR."""

from __future__ import annotations

from typing import Any, Literal

from .app import mcp
from .database import run_select


def _intervalo_clauses(
    data_inicio: str | None, data_fim: str | None
) -> tuple[str, list[Any]]:
    """Monta cláusula WHERE opcional para filtro por intervalo de datas."""
    clauses: list[str] = []
    params: list[Any] = []
    if data_inicio:
        clauses.append("so.date >= %s")
        params.append(data_inicio)
    if data_fim:
        clauses.append("so.date <= %s")
        params.append(data_fim)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    return where, params


@mcp.tool(
    name="executar_consulta_sql",
    description=(
        "Executa uma consulta SQL **somente leitura** (SELECT/WITH) na base de "
        "vendas e retorna as linhas. Comandos de escrita (INSERT, UPDATE, DELETE, "
        "DROP, ALTER, TRUNCATE, CREATE, COPY etc.) são bloqueados. Use esta tool "
        "para consultas ad-hoc; um LIMIT 1000 padrão é aplicado se nenhum LIMIT "
        "for informado."
    ),
)
def executar_consulta_sql(sql: str) -> list[dict[str, Any]]:
    """Executa uma consulta SELECT/WITH e retorna as linhas como lista de dicionários."""
    return run_select(sql)


@mcp.tool(
    name="listar_tabelas",
    description=(
        "Lista todas as tabelas do schema público da base de vendas, com a "
        "quantidade aproximada de linhas de cada uma."
    ),
)
def listar_tabelas() -> list[dict[str, Any]]:
    """Lista as tabelas do schema público."""
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
    return run_select(sql)


@mcp.tool(
    name="descrever_tabela",
    description=(
        "Retorna o nome, tipo e nulidade de cada coluna da tabela informada, "
        "para ajudar na construção de consultas SQL personalizadas."
    ),
)
def descrever_tabela(nome: str) -> list[dict[str, Any]]:
    """Retorna o schema (colunas, tipos) da tabela informada."""
    sql = """
        SELECT
            column_name AS coluna,
            data_type AS tipo,
            is_nullable AS aceita_nulo,
            column_default AS valor_padrao
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position
    """
    return run_select(sql, (nome,))


@mcp.tool(
    name="vendas_por_categoria",
    description=(
        "Agrega a receita total e quantidade de pedidos por categoria de produto. "
        "Aceita datas opcionais no formato AAAA-MM-DD para filtrar o intervalo."
    ),
)
def vendas_por_categoria(
    data_inicio: str | None = None,
    data_fim: str | None = None,
) -> list[dict[str, Any]]:
    """Receita e pedidos por categoria, opcionalmente filtrados por intervalo de datas."""
    where, params = _intervalo_clauses(data_inicio, data_fim)
    sql = f"""
        SELECT
            cat.name AS categoria,
            SUM(so.total_revenue) AS receita_total,
            SUM(so.units_sold) AS unidades_vendidas,
            COUNT(*) AS pedidos
        FROM sales_order so
        JOIN product p ON p.id = so.product_id
        JOIN category cat ON cat.id = p.category_id
        {where}
        GROUP BY cat.name
        ORDER BY receita_total DESC
    """
    return run_select(sql, tuple(params))


@mcp.tool(
    name="vendas_por_regiao",
    description=(
        "Agrega a receita total e quantidade de pedidos por região geográfica. "
        "Aceita datas opcionais no formato AAAA-MM-DD para filtrar o intervalo."
    ),
)
def vendas_por_regiao(
    data_inicio: str | None = None,
    data_fim: str | None = None,
) -> list[dict[str, Any]]:
    """Receita e pedidos por região, opcionalmente filtrados por intervalo de datas."""
    where, params = _intervalo_clauses(data_inicio, data_fim)
    sql = f"""
        SELECT
            r.name AS regiao,
            SUM(so.total_revenue) AS receita_total,
            SUM(so.units_sold) AS unidades_vendidas,
            COUNT(*) AS pedidos
        FROM sales_order so
        JOIN region r ON r.id = so.region_id
        {where}
        GROUP BY r.name
        ORDER BY receita_total DESC
    """
    return run_select(sql, tuple(params))


@mcp.tool(
    name="vendas_por_metodo_pagamento",
    description=(
        "Agrega a receita total e quantidade de pedidos por método de pagamento. "
        "Aceita datas opcionais no formato AAAA-MM-DD para filtrar o intervalo."
    ),
)
def vendas_por_metodo_pagamento(
    data_inicio: str | None = None,
    data_fim: str | None = None,
) -> list[dict[str, Any]]:
    """Receita e pedidos por método de pagamento."""
    where, params = _intervalo_clauses(data_inicio, data_fim)
    sql = f"""
        SELECT
            pm.name AS metodo_pagamento,
            SUM(so.total_revenue) AS receita_total,
            SUM(so.units_sold) AS unidades_vendidas,
            COUNT(*) AS pedidos
        FROM sales_order so
        JOIN payment_method pm ON pm.id = so.payment_method_id
        {where}
        GROUP BY pm.name
        ORDER BY receita_total DESC
    """
    return run_select(sql, tuple(params))


@mcp.tool(
    name="vendas_por_periodo",
    description=(
        "Agrega a receita total por período (dia, mês ou ano) para identificar "
        "tendências e sazonalidade. Granularidade aceita: 'dia', 'mes' ou 'ano'."
    ),
)
def vendas_por_periodo(
    granularidade: Literal["dia", "mes", "ano"] = "mes",
    data_inicio: str | None = None,
    data_fim: str | None = None,
) -> list[dict[str, Any]]:
    """Receita por período usando date_trunc."""
    mapa = {"dia": "day", "mes": "month", "ano": "year"}
    if granularidade not in mapa:
        raise ValueError("granularidade deve ser 'dia', 'mes' ou 'ano'.")

    where, params = _intervalo_clauses(data_inicio, data_fim)
    sql = f"""
        SELECT
            date_trunc('{mapa[granularidade]}', so.date)::date AS periodo,
            SUM(so.total_revenue) AS receita_total,
            SUM(so.units_sold) AS unidades_vendidas,
            COUNT(*) AS pedidos
        FROM sales_order so
        {where}
        GROUP BY periodo
        ORDER BY periodo
    """
    return run_select(sql, tuple(params))


@mcp.tool(
    name="top_produtos",
    description=(
        "Lista os produtos mais vendidos. Use 'receita' para ordenar pelo total "
        "faturado, ou 'unidades' para ordenar pela quantidade vendida. "
        "O parâmetro `limite` controla quantos produtos retornar (padrão: 10)."
    ),
)
def top_produtos(
    limite: int = 10,
    ordenar_por: Literal["receita", "unidades"] = "receita",
    data_inicio: str | None = None,
    data_fim: str | None = None,
) -> list[dict[str, Any]]:
    """Top N produtos por receita ou unidades."""
    if ordenar_por not in ("receita", "unidades"):
        raise ValueError("ordenar_por deve ser 'receita' ou 'unidades'.")
    if limite <= 0 or limite > 1000:
        raise ValueError("limite deve estar entre 1 e 1000.")

    where, params = _intervalo_clauses(data_inicio, data_fim)
    coluna = "receita_total" if ordenar_por == "receita" else "unidades_vendidas"
    sql = f"""
        SELECT
            p.name AS produto,
            cat.name AS categoria,
            SUM(so.total_revenue) AS receita_total,
            SUM(so.units_sold) AS unidades_vendidas,
            COUNT(*) AS pedidos
        FROM sales_order so
        JOIN product p ON p.id = so.product_id
        JOIN category cat ON cat.id = p.category_id
        {where}
        GROUP BY p.name, cat.name
        ORDER BY {coluna} DESC
        LIMIT %s
    """
    return run_select(sql, (*params, limite), apply_default_limit=False)
