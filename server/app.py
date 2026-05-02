"""Instância única do FastMCP usada pelos módulos de tools, resources e prompts."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-salesdatabase")

# Importações com efeito colateral: registram tools/resources/prompts via decoradores.
from . import tools, resources, prompts  # noqa: E402,F401
