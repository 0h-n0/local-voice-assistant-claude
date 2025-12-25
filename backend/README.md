# Local Voice Assistant - Backend

FastAPI backend for the Local Voice Assistant project.

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

## Setup

```bash
# Install dependencies
uv sync --all-extras

# Verify installation
uv run ruff check .
uv run mypy --strict src/

# Run tests
uv run pytest
```

## Development

```bash
# Start development server
uv run uvicorn src.main:app --reload --port 8000

# Check health endpoint
curl http://localhost:8000/health
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |

## Quality Checks

```bash
# Linting
uv run ruff check .

# Formatting
uv run ruff format .

# Type checking
uv run mypy --strict src/

# Tests
uv run pytest
```
