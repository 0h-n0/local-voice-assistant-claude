# Phase 0 Research: TTS API (Text-to-Speech)

**Date**: 2025-12-26
**Feature**: [spec.md](./spec.md) | [plan.md](./plan.md)

## 1. Technology Analysis

### Style-Bert-VITS2 Overview

Style-Bert-VITS2 は [Bert-VITS2](https://github.com/fishaudio/Bert-VITS2) をベースに、音声スタイルの制御機能を追加した日本語 TTS モデル。

**Key Features**:
- 感情・話し方スタイルの自由な制御
- CPU のみでも推論可能（GPU なしで動作）
- Python ライブラリとして `pip install` 可能
- ローカル推論のみ（外部 API 通信なし）

**License**: AGPL-3.0（[litagin02/Style-Bert-VITS2](https://github.com/litagin02/Style-Bert-VITS2)）

### Installation

```bash
# 推論のみ（ライブラリとして使用）
pip install style-bert-vits2

# または uv を使用
uv add style-bert-vits2
```

### Required Model Files

推論には以下のファイルが必要：

```
model_assets/
└── your_model/
    ├── config.json          # モデル設定
    ├── *.safetensors        # モデルウェイト
    └── style_vectors.npy    # スタイルベクトル
```

事前学習済みモデルは Hugging Face Hub から取得可能。

## 2. API Reference

### Core Classes

#### TTSModel

メインの音声合成クラス。

```python
from style_bert_vits2.tts_model import TTSModel
from pathlib import Path

model = TTSModel(
    model_path=Path("model_assets/model.safetensors"),
    config_path=Path("model_assets/config.json"),
    style_vec_path=Path("model_assets/style_vectors.npy"),
    device="cpu",  # or "cuda"
)
```

#### BERT Models (Required)

推論前に BERT トークナイザーとモデルをロードする必要がある：

```python
from style_bert_vits2.nlp import bert_models
from style_bert_vits2.constants import Languages

# 日本語モデルのロード
bert_models.load_model(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")
bert_models.load_tokenizer(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")
```

### Inference Method

```python
def infer(
    text: str,
    language: Languages = Languages.JP,
    speaker_id: int = 0,
    reference_audio_path: Optional[str] = None,
    sdp_ratio: float = DEFAULT_SDP_RATIO,
    noise: float = DEFAULT_NOISE,
    noise_w: float = DEFAULT_NOISEW,
    length: float = DEFAULT_LENGTH,           # 話速制御 (1.0 = 通常)
    style: str = DEFAULT_STYLE,
    style_weight: float = DEFAULT_STYLE_WEIGHT,
    pitch_scale: float = 1.0,
    intonation_scale: float = 1.0,
) -> tuple[int, NDArray[Any]]
```

**Returns**: `(sampling_rate, audio_data)` - 16-bit PCM

**Key Parameters**:
| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `length` | 話速スケール（小さいほど速い） | 1.0 | 0.5-2.0 |
| `sdp_ratio` | SDP/DP 混合比（高いほど抑揚変化大） | 0.2 | 0.0-1.0 |
| `noise` | DP ノイズ | 0.6 | 0.0-1.0 |
| `noise_w` | SDP ノイズ | 0.8 | 0.0-1.0 |

### Complete Usage Example

```python
from pathlib import Path
import numpy as np
from scipy.io import wavfile

from style_bert_vits2.nlp import bert_models
from style_bert_vits2.constants import Languages
from style_bert_vits2.tts_model import TTSModel

# 1. BERT モデルのロード（起動時に一度だけ）
bert_models.load_model(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")
bert_models.load_tokenizer(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")

# 2. TTS モデルの初期化
model = TTSModel(
    model_path=Path("model_assets/jvnv-F1-jp/jvnv-F1-jp_e160_s14000.safetensors"),
    config_path=Path("model_assets/jvnv-F1-jp/config.json"),
    style_vec_path=Path("model_assets/jvnv-F1-jp/style_vectors.npy"),
    device="cpu",
)

# 3. 音声合成
sr, audio = model.infer(
    text="こんにちは、音声アシスタントです。",
    language=Languages.JP,
    length=1.0,  # 通常速度
)

# 4. WAV 出力
wavfile.write("output.wav", sr, audio)
```

## 3. Integration Design

### Service Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  FastAPI Router │────▶│   TTSService    │────▶│   TTSModel      │
│   /api/tts/*    │     │  (singleton)    │     │ Style-Bert-VITS2│
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Key Design Decisions

1. **Singleton Model Loading**
   - BERT モデルと TTS モデルはアプリケーション起動時に一度だけロード
   - メモリ効率とレイテンシ削減のため

2. **Synchronous Inference**
   - Style-Bert-VITS2 の推論は同期的
   - FastAPI では `run_in_executor` でブロッキング回避

3. **Concurrency Control**
   - `asyncio.Semaphore` で同時リクエスト数を制限（1-3）
   - GPU メモリ/CPU 負荷の過負荷防止

4. **WAV Output**
   - `scipy.io.wavfile` で WAV 形式出力
   - 16-bit PCM、サンプリングレートはモデル依存（通常 44100Hz）

## 4. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| モデルロード時間が長い | High | 起動時ロード、ヘルスチェックで状態確認 |
| メモリ使用量大 | Medium | 単一モデルのみロード、モニタリング |
| CPU 推論が遅い | Medium | GPU 対応、タイムアウト設定 |
| BERT モデルダウンロード失敗 | High | 事前ダウンロード、エラーハンドリング |

## 5. Dependencies

### Python Packages

```toml
# pyproject.toml
[project]
dependencies = [
    "style-bert-vits2>=2.5.0",
    "torch>=2.0.0",
    "scipy>=1.10.0",
]
```

### External Resources

- BERT Model: `ku-nlp/deberta-v2-large-japanese-char-wwm` (Hugging Face Hub)
- TTS Model: 事前にローカルに配置（例: `jvnv-F1-jp`）

## 6. Testing Strategy

### Unit Tests
- `TTSService` のパラメータ検証
- エラーハンドリング（空テキスト、長すぎるテキスト）

### Integration Tests
- API エンドポイント経由での音声生成
- WAV ファイル形式の検証

### Mock Strategy
- `TTSModel.infer()` をモックして高速テスト
- 実際のモデルロードは CI でスキップ可能に

## Sources

- [GitHub - litagin02/Style-Bert-VITS2](https://github.com/litagin02/Style-Bert-VITS2)
- [style-bert-vits2 on PyPI](https://pypi.org/project/style-bert-vits2/)
- [Style-Bert-VITS2 tts_model.py](https://github.com/litagin02/Style-Bert-VITS2/blob/master/style_bert_vits2/tts_model.py)
- [Style-Bert-VITS2 library.ipynb](https://github.com/litagin02/Style-Bert-VITS2/blob/master/library.ipynb)
