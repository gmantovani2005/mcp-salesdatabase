"""Prompts MCP em PT-BR para orientar análises de vendas."""

from __future__ import annotations

from typing import Literal

from .app import mcp


@mcp.prompt(
    name="analise_geral_vendas",
    description=(
        "Conduz uma análise consolidada da base de vendas: receita por categoria, "
        "região e top produtos."
    ),
)
def analise_geral_vendas() -> str:
    return (
        "Você é um analista de dados especializado em vendas online. "
        "Use as tools disponíveis no MCP `mcp-salesdatabase` para construir uma "
        "análise consolidada da base de vendas. Siga este roteiro:\n\n"
        "1. Liste as tabelas com `listar_tabelas` e confirme o schema relevante.\n"
        "2. Use `vendas_por_categoria` para identificar as categorias com maior receita.\n"
        "3. Use `vendas_por_regiao` para destacar as regiões mais relevantes.\n"
        "4. Use `top_produtos` (limite=10, ordenar_por='receita') para listar os "
        "produtos campeões de receita.\n"
        "5. Apresente um resumo executivo em **português**, com bullets, números "
        "absolutos e percentuais sobre o total.\n"
        "6. Sugira 3 próximos passos analíticos baseados nos achados.\n"
    )


@mcp.prompt(
    name="tendencia_temporal",
    description=(
        "Analisa a evolução temporal da receita para identificar sazonalidade e "
        "tendências de crescimento."
    ),
)
def tendencia_temporal(
    granularidade: Literal["dia", "mes", "ano"] = "mes",
) -> str:
    return (
        f"Analise a tendência temporal das vendas com granularidade '{granularidade}' "
        "usando a tool `vendas_por_periodo`. A partir do resultado:\n\n"
        "1. Identifique períodos de pico e de queda.\n"
        "2. Indique se há padrão sazonal aparente.\n"
        "3. Calcule a variação percentual entre o primeiro e o último período.\n"
        "4. Sugira hipóteses para os comportamentos observados.\n\n"
        "Responda em **português**, com gráfico textual (ASCII bars) opcional e "
        "tabela resumo dos períodos mais relevantes."
    )


@mcp.prompt(
    name="comparativo_regional",
    description=(
        "Compara o desempenho de vendas entre regiões, opcionalmente focando em "
        "uma categoria específica."
    ),
)
def comparativo_regional(categoria: str | None = None) -> str:
    foco = (
        f" Foque a análise na categoria **{categoria}** filtrando os resultados."
        if categoria
        else ""
    )
    return (
        "Faça um comparativo regional das vendas." + foco + "\n\n"
        "Roteiro:\n"
        "1. Use `vendas_por_regiao` para receita total por região.\n"
        "2. Para cada região, use `executar_consulta_sql` se necessário para "
        "detalhar as 3 categorias mais fortes (JOIN entre `sales_order`, "
        "`product`, `category`, `region`).\n"
        "3. Aponte regiões com desempenho acima/abaixo da média e possíveis "
        "explicações.\n"
        "4. Sugira ações de marketing regional baseadas nos padrões.\n\n"
        "Responda em **português** com bullets e uma tabela final de resumo."
    )


@mcp.prompt(
    name="desempenho_produto",
    description=(
        "Analisa o desempenho dos produtos, identificando campeões de venda e "
        "candidatos a otimização de inventário."
    ),
)
def desempenho_produto(categoria: str | None = None) -> str:
    foco = (
        f" Concentre a análise na categoria **{categoria}**."
        if categoria
        else ""
    )
    return (
        "Avalie o desempenho dos produtos da base de vendas." + foco + "\n\n"
        "Passos:\n"
        "1. Liste os 10 produtos com maior receita usando `top_produtos`.\n"
        "2. Liste os 10 produtos com maior volume de unidades vendidas "
        "(`top_produtos` com `ordenar_por='unidades'`).\n"
        "3. Identifique produtos presentes em apenas uma das listas — "
        "podem indicar produtos de ticket alto x produtos de giro alto.\n"
        "4. Sugira recomendações de inventário e marketing para cada perfil.\n\n"
        "Responda em **português**, com tabela final destacando o ticket médio "
        "(receita_total / unidades_vendidas) de cada produto."
    )


@mcp.prompt(
    name="analise_metodo_pagamento",
    description=(
        "Avalia como diferentes métodos de pagamento influenciam a receita e o "
        "ticket médio."
    ),
)
def analise_metodo_pagamento() -> str:
    return (
        "Analise o impacto dos métodos de pagamento sobre as vendas:\n\n"
        "1. Use `vendas_por_metodo_pagamento` para receita, unidades e número "
        "de pedidos por método.\n"
        "2. Calcule o ticket médio por método (receita_total / pedidos).\n"
        "3. Identifique o método dominante e métodos sub-utilizados.\n"
        "4. Levante hipóteses sobre o porquê e sugira testes A/B ou campanhas "
        "para diversificar a aceitação.\n\n"
        "Responda em **português** com bullets e uma tabela final."
    )
