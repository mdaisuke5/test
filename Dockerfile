FROM python:3.11-slim

ENV POETRY_VERSION=1.8.3
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"
WORKDIR /app
COPY pyproject.toml README.md .
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi
COPY src ./src
COPY run_backtest.sh run_paper.sh run_live.sh ./
CMD ["/bin/bash", "./run_live.sh"]
