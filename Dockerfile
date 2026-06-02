
#cria uma imagem a partir da imagem base do python 3.13 slim
FROM python:3.13-slim


#define o diretório de trabalho dentro do container
ENV POETRY_VIRTUALENV_CREATE=false

#instala as dependências do sistema necessárias para o projeto
WORKDIR /app


#copia os arquivos de configuração do projeto para o diretório de trabalho
COPY . .


#instala as dependências do projeto usando o poetry
RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install --without dev --no-interaction --no-ansi
#configura o poetry para usar no máximo 10 workers durante a instalação das dependências
RUN poetry config installer.max-workers 10


#instala as dependências do projeto, ignorando as dependências de desenvolvimento
RUN chmod +x ./entrypoint.sh

#expõe a porta 8000 para acesso externo
EXPOSE 8000


#define o comando de entrada para iniciar a aplicação usando o uvicorn
ENTRYPOINT ["./entrypoint.sh"]