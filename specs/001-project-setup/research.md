# Research: Project Setup - Backend & Frontend Foundation

**Date**: 2025-12-25
**Feature**: 001-project-setup

## Overview

このドキュメントは、プロジェクトセットアップに必要な技術選択の調査結果をまとめたものです。

## Backend: Python Project Structure

### Decision: uv + FastAPI + Pydantic v2

**Rationale**:
- `uv` は憲法で必須指定されており、高速なパッケージ解決と依存関係管理を提供
- FastAPI は非同期処理をネイティブサポートし、Pydantic v2と統合済み
- Pydantic v2 はパフォーマンスが大幅に向上し、strictモードで型安全性を確保

**Alternatives Considered**:
| Alternative | Reason Rejected |
|-------------|-----------------|
| pip + requirements.txt | 憲法違反（uv必須） |
| poetry | 憲法違反（uv必須） |
| Flask | 非同期サポートが限定的、型統合が弱い |
| Django | オーバーエンジニアリング、シンプルさ原則に反する |

### pyproject.toml Configuration

```toml
[project]
name = "local-voice-assistant-backend"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.109.0",
    "pydantic>=2.5.0",
    "uvicorn[standard]>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.26.0",
    "mypy>=1.8.0",
    "ruff>=0.1.0",
]

[tool.ruff]
target-version = "py311"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]

[tool.mypy]
python_version = "3.11"
strict = true
```

## Frontend: Next.js Project Structure

### Decision: Next.js 14+ (App Router) + TypeScript

**Rationale**:
- Next.js App Router は最新のReactパターンをサポート
- TypeScript strict mode で型安全性を確保
- 憲法で指定されたESLint + Prettierと統合

**Alternatives Considered**:
| Alternative | Reason Rejected |
|-------------|-----------------|
| Create React App | 非推奨、Next.jsがデファクトスタンダード |
| Vite + React | SSR非対応、将来の拡張性に制限 |
| Pages Router | 旧式、App Routerが推奨 |

### Next.js Configuration

- TypeScript: strict mode
- ESLint: Next.js recommended + import rules
- Prettier: 統一フォーマット
- Jest: React Testing Library統合

## Testing Strategy

### Backend Testing

| Test Type | Tool | Purpose |
|-----------|------|---------|
| Unit | pytest | 個別関数・クラスのテスト |
| Integration | pytest + httpx | API統合テスト |
| Contract | pytest | APIレスポンス形式の検証 |

### Frontend Testing

| Test Type | Tool | Purpose |
|-----------|------|---------|
| Unit | Jest + RTL | コンポーネントテスト |
| Integration | Jest + RTL | ページレベルテスト |

## CORS Configuration

### Decision: Development CORS許可

**Configuration**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Rationale**:
- 開発環境でフロントエンド（:3000）からバックエンド（:8000）への呼び出しを許可
- 本番環境では適切なオリジン制限を設定（将来機能で対応）

## Health Check Endpoint

### Decision: 標準的なヘルスチェックパターン

**Response Model**:
```python
class HealthResponse(BaseModel):
    status: Literal["healthy", "unhealthy"]
    version: str
    timestamp: datetime
```

**Rationale**:
- シンプルで標準的なヘルスチェック形式
- 将来の拡張（依存サービスのチェック等）に対応可能

## Dependencies Summary

### Backend (pyproject.toml)

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | >=0.109.0 | Web framework |
| pydantic | >=2.5.0 | Data validation |
| uvicorn | >=0.27.0 | ASGI server |
| pytest | >=7.4.0 | Testing |
| pytest-asyncio | >=0.23.0 | Async test support |
| httpx | >=0.26.0 | Test client |
| mypy | >=1.8.0 | Type checking |
| ruff | >=0.1.0 | Linting/formatting |

### Frontend (package.json)

| Package | Version | Purpose |
|---------|---------|---------|
| next | ^14.0.0 | Framework |
| react | ^18.0.0 | UI library |
| typescript | ^5.0.0 | Language |
| jest | ^29.0.0 | Testing |
| @testing-library/react | ^14.0.0 | Component testing |
| eslint | ^8.0.0 | Linting |
| prettier | ^3.0.0 | Formatting |

---

*Research completed - all technical decisions documented*
