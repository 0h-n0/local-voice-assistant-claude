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

- Python 3.11+
- Node.js 18+
- [uv](https://docs.astral.sh/uv/) (Python package manager)

### Backend Setup

```bash
cd backend
uv sync
uv run uvicorn src.main:app --reload
```

The backend will be available at http://localhost:8000

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:3000

### Running Both Services

Open two terminal windows:

**Terminal 1 - Backend:**
```bash
cd backend
uv run uvicorn src.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
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
- Python 3.11+
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
