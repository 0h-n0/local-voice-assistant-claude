# Local Voice Assistant

A privacy-first local voice assistant with FastAPI backend and Next.js frontend.

## Project Structure

```
local-voice-assistant-claude/
├── backend/          # FastAPI backend (Python)
├── frontend/         # Next.js frontend (TypeScript)
├── specs/            # Feature specifications
└── .specify/         # Project templates and configuration
```

## Quick Start

### Prerequisites

- Python 3.11 or 3.12 (Python 3.13+ is not currently supported due to dependency constraints)
- Node.js 18+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- GNU Make

### One-Command Setup

```bash
# Install all dependencies
make install

# Start all services (backend + frontend)
make dev
```

This starts:
- **Backend**: http://localhost:8000 (FastAPI with hot reload)
- **Frontend**: http://localhost:3000 (Next.js dev server)

Press `Ctrl+C` to stop all services.

### Available Make Commands

```bash
make help       # Show all available commands
make dev        # Start all services with hot reload
make backend    # Start backend only
make frontend   # Start frontend only
make down       # Stop all running services
make install    # Install all dependencies
make check-deps # Verify required tools are installed
make clean      # Stop services and clean temp files
```

### Manual Setup (Alternative)

If you prefer to run services separately:

**Backend:**
```bash
cd backend
uv sync
uv run uvicorn src.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Development

### Backend Commands

```bash
cd backend

# Run development server
uv run uvicorn src.main:app --reload

# Run tests
uv run pytest

# Run linter
uv run ruff check .

# Run type checker
uv run mypy --strict src/
```

### Frontend Commands

```bash
cd frontend

# Run development server
npm run dev

# Run tests
npm test

# Run linter
npm run lint

# Build for production
npm run build
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check endpoint |

## Technology Stack

### Backend
- FastAPI
- Python 3.11-3.12
- Pydantic v2
- uv (package manager)
- ruff (linter/formatter)
- mypy (type checker)
- pytest (testing)

### Frontend
- Next.js 16 (App Router)
- React 19
- TypeScript (strict mode)
- Tailwind CSS
- Jest + React Testing Library

## License

MIT
