FROM python:3.14-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

# Instala uv (gerenciador de dependências Python)
RUN pip install --no-cache-dir uv

WORKDIR /app

# Instala dependências em camada separada para aproveitar cache
COPY pyproject.toml ./
RUN uv lock && uv sync --frozen --no-dev

# Copia o código da aplicação
COPY main.py ./
COPY server ./server
COPY docs ./docs

ENV MCP_TRANSPORT=sse \
    MCP_SSE_HOST=0.0.0.0 \
    MCP_SSE_PORT=8000

EXPOSE 8000

CMD ["uv", "run", "python", "main.py"]
