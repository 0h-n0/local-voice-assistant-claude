# local-voice-assistant-claude Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-12-26

## Active Technologies
- Python 3.11+ (Backend) + FastAPI, reazonspeech, NeMo, pydub (audio conversion), python-multipart (file upload) (002-stt-api)
- N/A (ステートレス処理、モデルはメモリに常駐) (002-stt-api)
- Python 3.11+ + FastAPI, Pydantic v2, OpenAI Python SDK, httpx (async HTTP) (003-llm-text-service)
- In-memory conversation cache (dict with TTL eviction) (003-llm-text-service)
- Python 3.11+ (Backend) + FastAPI, Pydantic v2, Style-Bert-VITS2, torch, scipy (004-tts-api)
- Python 3.11+ (Backend) + FastAPI, Pydantic v2, httpx (内部サービス呼び出し用) (005-voice-orchestrator)
- N/A（ステートレス処理、音声データは永続化しない） (005-voice-orchestrator)

- Python 3.11+ (Backend), TypeScript 5.x (Frontend)
- FastAPI, Pydantic v2, uvicorn (Backend)
- Next.js 16+, React 19+ (Frontend)

## Project Structure

```text
backend/
├── src/
│   ├── api/          # API endpoints
│   ├── models/       # Pydantic models
│   └── main.py       # FastAPI app
└── tests/            # pytest tests

frontend/
├── src/
│   ├── app/          # Next.js pages
│   ├── components/   # React components
│   ├── hooks/        # Custom hooks
│   ├── lib/          # Utilities
│   └── types/        # TypeScript types
└── tests/            # Jest tests
```

## Commands

### Backend

```bash
cd backend
uv run uvicorn src.main:app --reload  # Start dev server
uv run pytest                          # Run tests
uv run ruff check .                    # Lint
uv run mypy --strict src/              # Type check
```

### Frontend

```bash
cd frontend
npm run dev      # Start dev server
npm test         # Run tests
npm run lint     # Lint
```

## Code Style

- Python: Follow PEP 8, use type hints, docstrings required
- TypeScript: Strict mode, prefer functional components

## Recent Changes
- 005-voice-orchestrator: Added Python 3.11+ (Backend) + FastAPI, Pydantic v2, httpx (内部サービス呼び出し用)
- 004-tts-api: Added Python 3.11+ (Backend) + FastAPI, Pydantic v2, Style-Bert-VITS2, torch, scipy
- 003-llm-text-service: Added Python 3.11+ + FastAPI, Pydantic v2, OpenAI Python SDK, httpx (async HTTP)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
