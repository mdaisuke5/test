FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy dependency files if present
COPY pyproject.toml poetry.lock* /app/

RUN if [ -f pyproject.toml ]; then poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root; fi

COPY . /app

CMD ["python", "-m", "strategy"]
