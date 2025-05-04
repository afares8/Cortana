FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2

WORKDIR /app

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git java-common default-jre && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Instala Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copia solo archivos de dependencias para instalar antes
COPY pyproject.toml poetry.lock ./

# Instala dependencias del proyecto
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Copia el resto del proyecto
COPY . .

# Descarga modelo de spaCy
RUN python3 -m spacy download es_core_news_md

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

