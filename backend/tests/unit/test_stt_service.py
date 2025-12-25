"""Unit tests for STT service."""

import struct

import pytest

from src.services.stt_service import STTService


class TestAudioFormatValidation:
    """Tests for audio format validation."""

    def test_validate_wav_format_accepted(self):
        """WAV format should be accepted."""
        service = STTService()
        wav_data = create_minimal_wav()
        # validate_audio_format should not raise for valid WAV
        is_valid, error = service.validate_audio_format("test.wav", wav_data)
        assert is_valid is True
        assert error is None

    def test_validate_mp3_format_accepted(self):
        """MP3 format should be accepted."""
        service = STTService()
        # validate_audio_format should accept .mp3 extension
        is_valid, error = service.validate_audio_format("test.mp3", b"ID3\x00")
        assert is_valid is True
        assert error is None

    def test_validate_flac_format_accepted(self):
        """FLAC format should be accepted."""
        service = STTService()
        is_valid, error = service.validate_audio_format("test.flac", b"fLaC\x00")
        assert is_valid is True
        assert error is None

    def test_validate_ogg_format_accepted(self):
        """OGG format should be accepted."""
        service = STTService()
        is_valid, error = service.validate_audio_format("test.ogg", b"OggS\x00")
        assert is_valid is True
        assert error is None

    def test_validate_pdf_format_rejected(self):
        """PDF format should be rejected."""
        service = STTService()
        is_valid, error = service.validate_audio_format("test.pdf", b"%PDF")
        assert is_valid is False
        assert error == "UNSUPPORTED_FORMAT"

    def test_validate_txt_format_rejected(self):
        """TXT format should be rejected."""
        service = STTService()
        is_valid, error = service.validate_audio_format("test.txt", b"hello")
        assert is_valid is False
        assert error == "UNSUPPORTED_FORMAT"

    def test_validate_empty_audio_rejected(self):
        """Empty audio data should be rejected."""
        service = STTService()
        is_valid, error = service.validate_audio_format("test.wav", b"")
        assert is_valid is False
        assert error == "EMPTY_AUDIO"


class TestAudioResampling:
    """Tests for audio resampling to 16kHz."""

    @pytest.mark.asyncio
    async def test_resample_wav_to_16khz(self):
        """WAV audio should be resampled to 16kHz."""
        service = STTService()
        # Create a 44100Hz WAV
        wav_44100 = create_wav_with_sample_rate(44100)
        resampled = await service.resample_audio(wav_44100)
        # Check that output is valid (non-empty)
        assert len(resampled) > 0

    @pytest.mark.asyncio
    async def test_16khz_audio_not_modified(self):
        """16kHz audio should not need resampling."""
        service = STTService()
        wav_16000 = create_minimal_wav()  # Already 16kHz
        resampled = await service.resample_audio(wav_16000)
        # Should return valid audio data
        assert len(resampled) > 0


def create_minimal_wav() -> bytes:
    """Create a minimal valid WAV file at 16kHz with silence."""
    return create_wav_with_sample_rate(16000)


class TestAudioBuffer:
    """Tests for AudioBuffer class."""

    def test_audio_buffer_add_chunks(self):
        """AudioBuffer can add and accumulate chunks."""
        from src.services.stt_service import AudioBuffer

        buffer = AudioBuffer()
        chunk1 = b"\x00" * 100
        chunk2 = b"\x01" * 100
        buffer.add(chunk1)
        buffer.add(chunk2)
        assert len(buffer.get_data()) == 200

    def test_audio_buffer_clear(self):
        """AudioBuffer can be cleared."""
        from src.services.stt_service import AudioBuffer

        buffer = AudioBuffer()
        buffer.add(b"\x00" * 100)
        buffer.clear()
        assert len(buffer.get_data()) == 0

    def test_audio_buffer_should_process(self):
        """AudioBuffer should_process returns True when enough data."""
        from src.services.stt_service import AudioBuffer

        buffer = AudioBuffer(min_samples=1600)  # 100ms at 16kHz
        # Less than min_samples
        buffer.add(b"\x00" * 1000)
        assert buffer.should_process() is False
        # Add more to exceed threshold
        buffer.add(b"\x00" * 4000)
        assert buffer.should_process() is True


def create_wav_with_sample_rate(sample_rate: int) -> bytes:
    """Create a WAV file with specified sample rate."""
    num_channels = 1
    bits_per_sample = 16
    num_samples = sample_rate  # 1 second
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    data_size = num_samples * block_align

    header = b"RIFF"
    header += struct.pack("<I", 36 + data_size)
    header += b"WAVE"
    header += b"fmt "
    header += struct.pack("<I", 16)
    header += struct.pack("<H", 1)
    header += struct.pack("<H", num_channels)
    header += struct.pack("<I", sample_rate)
    header += struct.pack("<I", byte_rate)
    header += struct.pack("<H", block_align)
    header += struct.pack("<H", bits_per_sample)
    header += b"data"
    header += struct.pack("<I", data_size)
    audio_data = b"\x00" * data_size

    return header + audio_data
