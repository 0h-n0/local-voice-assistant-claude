# Contracts: ローカル開発環境セットアップ

本機能はMakefileベースの開発ツールであり、APIコントラクトは存在しません。

## Makefile Interface

代わりに、Makefileが提供するインターフェースを以下に定義します：

### Targets

| Target | Exit Code | stdout | stderr |
|--------|-----------|--------|--------|
| `make dev` | 0 (on clean exit) | Process logs | Error messages |
| `make backend` | 0 (on clean exit) | uvicorn logs | Error messages |
| `make frontend` | 0 (on clean exit) | Next.js logs | Error messages |
| `make down` | 0 | "Stopped all services" | Error messages |
| `make help` | 0 | Command list | - |

### Error Conditions

| Condition | Exit Code | Message |
|-----------|-----------|---------|
| Missing Python | 1 | "Error: Python 3.11+ is required" |
| Missing Node.js | 1 | "Error: Node.js 18+ is required" |
| Missing uv | 1 | "Error: uv is required. Install from https://github.com/astral-sh/uv" |
| Missing npm | 1 | "Error: npm is required" |
| Port in use | 1 | "Error: Port XXXX is already in use" |
