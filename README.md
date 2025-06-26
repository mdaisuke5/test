# Test Project

This repository contains example trading modules and a pytest suite.

## Development Setup

Install dependencies using [Poetry](https://python-poetry.org/):

```bash
poetry install
```

Run the linters and tests locally:

```bash
poetry run black --check .
poetry run ruff .
poetry run pytest
```
