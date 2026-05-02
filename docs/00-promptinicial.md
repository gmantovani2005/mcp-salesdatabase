## Objetivo
Criar um MCP que conecta a uma base de dados de vendas e retorne consultas SQL para análise dos dados.

## Contexto
* O arquivo `docs/data-sales.md` contém informações sobre a base de dados e insights que podem ser usadas para o projeto.
* O arquivo `docs/schema.sql` contém o schema da base de dados.
* O banco de dados foi criado em Postgresql e as informações de usuário e senham vão ser informados em arquivos .env.
* O Projeto ou repositório é Python e foi criado utilizando o comando `uv`.
* O MCP será usado em stdio em desenvolvimento e sse via container.

## Ação

* Crie o MCP que conecta a uma base de dados de vendas e retorne consultas SQL para análise dos dados.
* Utilize as informações dos arquivos `docs/data-sales.md` e `docs/schema.sql` para criar o MCP.
* Crie prompts, resources e tools em arquivos separados organizados em um diretório `server`.
* Utilize o MCP Inspector para que eu posso testar o MCP com o comando `uv run dev main.py`.
* As descriptions dos recursos precisam estar em Português do Brasil para alinhar os prompts dos usuários com as descrições. Os prompts vão estar em Português do Brasil também.
* Crie um diretório `.container` e adicione Dockerfile e arquivos YAML para o kubernetes (deployment e service). Arquivo `docker-compose.yaml` vai ser criado na raíz do projeto. Crie o `.dockerignore`.
* Documente o projeto no arquivo README.md.
* Crie o arquivo CLAUDE.md ao final como feito pelo comando `/init`.

