FROM python:3.12 as builder

WORKDIR /app

RUN pip install poetry
RUN poetry config virtualenvs.in-project true

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app/.venv .venv/
COPY . .

RUN apt-get update -y && apt-get install libpq5 -y && apt-get clean

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
