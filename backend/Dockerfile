FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    PATH="/opt/poetry/bin:$PATH"

WORKDIR /app

# Instala dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      curl \
      git \
      default-jre \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Instala Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

# Copia los archivos de dependencias primero
COPY pyproject.toml poetry.lock ./

# Instala dependencias del proyecto (sin crear venv adicional)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# ➤ Instalación de Playwright y navegadores
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      wget \
      libnss3 \
      libatk1.0-0 \
      libcups2 \
      libdrm2 \
      libxkbcommon0 \
      libx11-xcb1 \
      libxtst6 \
      libasound2 \
    && rm -rf /var/lib/apt/lists/* \
    && poetry run pip install playwright \
    && poetry run playwright install --with-deps

# Copia el resto del código fuente
COPY . .

# Descarga el modelo de spaCy para español
RUN python3 -m spacy download es_core_news_md

# Expone el puerto
EXPOSE 8000

# Comando de ejecución
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
