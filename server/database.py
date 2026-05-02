"""Acesso ao PostgreSQL com pool de conexões e validação somente-leitura."""

from __future__ import annotations

import os
import re
from typing import Any

from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

load_dotenv()

_READ_ONLY_PREFIX = re.compile(r"^\s*(select|with)\b", re.IGNORECASE)
_FORBIDDEN_KEYWORDS = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|grant|revoke|create|copy|vacuum|reindex|comment|call)\b",
    re.IGNORECASE,
)
_HAS_LIMIT = re.compile(r"\blimit\s+\d+\b", re.IGNORECASE)

DEFAULT_LIMIT = 1000

_pool: ConnectionPool | None = None


def _conninfo() -> str:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "salesdb")
    user = os.getenv("POSTGRES_USER", "salesuser")
    password = os.getenv("POSTGRES_PASSWORD", "")
    return f"host={host} port={port} dbname={db} user={user} password={password}"


def get_pool() -> ConnectionPool:
    """Retorna o pool de conexões, criando-o sob demanda."""
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            conninfo=_conninfo(),
            min_size=1,
            max_size=int(os.getenv("POSTGRES_POOL_MAX", "5")),
            kwargs={"autocommit": True},
            open=True,
        )
    return _pool


def _ensure_select_only(sql: str) -> None:
    """Valida que a query é somente leitura. Lança ValueError caso contrário."""
    stripped = sql.strip().rstrip(";")
    if ";" in stripped:
        raise ValueError("Apenas uma instrução SQL é permitida (sem ';' interno).")
    if not _READ_ONLY_PREFIX.match(stripped):
        raise ValueError("Somente queries SELECT/WITH são permitidas.")
    if _FORBIDDEN_KEYWORDS.search(stripped):
        raise ValueError(
            "Comando não permitido. A consulta deve ser apenas leitura (SELECT/WITH)."
        )


def _apply_default_limit(sql: str, limit: int = DEFAULT_LIMIT) -> str:
    if _HAS_LIMIT.search(sql):
        return sql
    return f"{sql.rstrip().rstrip(';')} LIMIT {limit}"


def run_select(
    sql: str,
    params: tuple[Any, ...] | dict[str, Any] | None = None,
    *,
    enforce_read_only: bool = True,
    apply_default_limit: bool = True,
) -> list[dict[str, Any]]:
    """Executa uma consulta SELECT/WITH e retorna a lista de linhas (dicts).

    - `enforce_read_only=True` recusa comandos que não sejam SELECT/WITH.
    - `apply_default_limit=True` adiciona `LIMIT 1000` se a query não tiver LIMIT.
    """
    if enforce_read_only:
        _ensure_select_only(sql)

    final_sql = _apply_default_limit(sql) if apply_default_limit else sql

    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(final_sql, params)
            rows = cur.fetchall()
    return [dict(r) for r in rows]
