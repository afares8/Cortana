FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    PATH="/opt/poetry/bin:$PATH"

WORKDIR /app

# Instala dependencias del sistema necesarias para:
# - WeasyPrint (cairo, pango, gobject, gdk-pixbuf, glib)
# - base del sistema (git, curl, jre)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      curl \
      git \
      default-jre \
      libpango-1.0-0 \
      libpangoft2-1.0-0 \
      libcairo2 \
      libpq-dev \
      libffi-dev \
      libjpeg-dev \
      libopenjp2-7-dev \
      libnss3 \
      libatk1.0-0 \
      libcups2 \
      libdrm2 \
      libxkbcommon0 \
      libx11-xcb1 \
      libxtst6 \
      libasound2 \
      libgdk-pixbuf2.0-0 \
      shared-mime-info \
      libxml2 \
      libxslt1.1 \
      libglib2.0-0 \
      libgirepository1.0-dev \
      wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Instala Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

# Copia el código completo
COPY . .

# Instala dependencias del proyecto (sin crear virtualenv)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Instala Playwright y navegadores necesarios
RUN poetry run pip install playwright && \
    poetry run playwright install --with-deps

# Descarga el modelo de spaCy en español
RUN python3 -m spacy download es_core_news_md

# Expone el puerto del backend
EXPOSE 8000

# Comando por defecto al ejecutar el contenedor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
