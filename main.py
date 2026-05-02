"""Entrypoint do MCP de análise de vendas.

Em desenvolvimento usa stdio (modo padrão); em container usa SSE.
A escolha é controlada pela variável de ambiente `MCP_TRANSPORT`
(`stdio` ou `sse`).
"""

from __future__ import annotations

import os

from server.app import mcp


def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()

    if transport == "sse":
        mcp.settings.host = os.getenv("MCP_SSE_HOST", "0.0.0.0")
        mcp.settings.port = int(os.getenv("MCP_SSE_PORT", "8000"))
        mcp.run(transport="sse")
    elif transport == "stdio":
        mcp.run(transport="stdio")
    else:
        raise SystemExit(
            f"MCP_TRANSPORT inválido: {transport!r}. Use 'stdio' ou 'sse'."
        )


if __name__ == "__main__":
    main()
