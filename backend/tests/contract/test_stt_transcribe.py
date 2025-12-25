"""Contract tests for POST /api/stt/transcribe endpoint."""

import io

import pytest


@pytest.mark.asyncio
async def test_transcribe_returns_json_with_text_field(client):
    """POST /api/stt/transcribe returns JSON with text field."""
    # Create a minimal valid WAV file (8 bytes header + empty data)
    wav_content = create_minimal_wav()
    files = {"file": ("test.wav", io.BytesIO(wav_content), "audio/wav")}

    response = await client.post("/api/stt/transcribe", files=files)

    # Should return 200 with transcription response
    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert "duration_seconds" in data
    assert "processing_time_seconds" in data


@pytest.mark.asyncio
async def test_transcribe_rejects_unsupported_format(client):
    """POST /api/stt/transcribe rejects unsupported file formats."""
    files = {"file": ("test.pdf", io.BytesIO(b"fake pdf content"), "application/pdf")}

    response = await client.post("/api/stt/transcribe", files=files)

    assert response.status_code == 400
    data = response.json()
    # Error is wrapped in detail
    detail = data.get("detail", data)
    assert detail["error_code"] == "UNSUPPORTED_FORMAT"


@pytest.mark.asyncio
async def test_transcribe_accepts_mp3_format(client):
    """POST /api/stt/transcribe accepts MP3 format."""
    # Create a minimal MP3 file (ID3 header)
    mp3_content = b"ID3" + b"\x00" * 100
    files = {"file": ("test.mp3", io.BytesIO(mp3_content), "audio/mpeg")}

    response = await client.post("/api/stt/transcribe", files=files)

    # MP3 should be accepted (may fail in transcription but not format check)
    # We check it doesn't return UNSUPPORTED_FORMAT
    if response.status_code == 400:
        data = response.json()
        assert data["error_code"] != "UNSUPPORTED_FORMAT"


@pytest.mark.asyncio
async def test_transcribe_rejects_empty_file(client):
    """POST /api/stt/transcribe rejects empty audio files."""
    files = {"file": ("test.wav", io.BytesIO(b""), "audio/wav")}

    response = await client.post("/api/stt/transcribe", files=files)

    assert response.status_code == 400
    data = response.json()
    # Error is wrapped in detail
    detail = data.get("detail", data)
    assert detail["error_code"] == "EMPTY_AUDIO"


def create_minimal_wav() -> bytes:
    """Create a minimal valid WAV file with silence."""
    import struct

    # WAV file parameters
    num_channels = 1
    sample_rate = 16000
    bits_per_sample = 16
    num_samples = sample_rate  # 1 second of audio
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    data_size = num_samples * block_align

    # Create WAV header
    header = b"RIFF"
    header += struct.pack("<I", 36 + data_size)  # File size - 8
    header += b"WAVE"
    header += b"fmt "
    header += struct.pack("<I", 16)  # fmt chunk size
    header += struct.pack("<H", 1)  # Audio format (PCM)
    header += struct.pack("<H", num_channels)
    header += struct.pack("<I", sample_rate)
    header += struct.pack("<I", byte_rate)
    header += struct.pack("<H", block_align)
    header += struct.pack("<H", bits_per_sample)
    header += b"data"
    header += struct.pack("<I", data_size)

    # Add silence (zeros)
    audio_data = b"\x00" * data_size

    return header + audio_data
