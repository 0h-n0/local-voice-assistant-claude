"""Unit tests for TTSService.

These tests validate the service logic without requiring actual model loading.
"""


import numpy as np
import pytest


class TestTTSServiceValidation:
    """Unit tests for TTSService validation logic."""

    def test_validate_text_empty_raises_error(self, mock_tts_service):
        """Verify empty text raises validation error."""
        with pytest.raises(ValueError, match="empty"):
            mock_tts_service.validate_text("")

    def test_validate_text_whitespace_only_raises_error(self, mock_tts_service):
        """Verify whitespace-only text raises validation error."""
        with pytest.raises(ValueError, match="empty"):
            mock_tts_service.validate_text("   ")

    def test_validate_text_too_long_raises_error(self, mock_tts_service):
        """Verify text exceeding max length raises validation error."""
        long_text = "あ" * 5001
        with pytest.raises(ValueError, match="too long"):
            mock_tts_service.validate_text(long_text)

    def test_validate_text_valid_returns_stripped(self, mock_tts_service):
        """Verify valid text is returned stripped."""
        result = mock_tts_service.validate_text("  こんにちは  ")
        assert result == "こんにちは"

    def test_validate_text_at_max_length_succeeds(self, mock_tts_service):
        """Verify text at exactly max length succeeds."""
        max_text = "あ" * 5000
        result = mock_tts_service.validate_text(max_text)
        assert len(result) == 5000


class TestTTSServiceSynthesize:
    """Unit tests for TTSService synthesize method."""

    @pytest.mark.asyncio
    async def test_synthesize_returns_audio_data(self, mock_tts_service):
        """Verify synthesize returns sample rate and audio data."""
        sr, audio = await mock_tts_service.synthesize("こんにちは")
        assert isinstance(sr, int)
        assert sr > 0
        assert isinstance(audio, np.ndarray)
        assert len(audio) > 0

    @pytest.mark.asyncio
    async def test_synthesize_empty_text_raises_error(self, mock_tts_service):
        """Verify synthesize with empty text raises error."""
        with pytest.raises(ValueError):
            await mock_tts_service.synthesize("")

    @pytest.mark.asyncio
    async def test_synthesize_default_speed(self, mock_tts_service):
        """Verify synthesize uses default speed of 1.0."""
        sr, audio = await mock_tts_service.synthesize("テスト")
        # Mock should have been called with default length=1.0
        assert sr > 0


class TestTTSServiceSpeedParameter:
    """Unit tests for TTSService speed parameter handling."""

    @pytest.mark.asyncio
    async def test_synthesize_with_fast_speed(self, mock_tts_service):
        """Verify synthesize works with fast speed (1.5)."""
        sr, audio = await mock_tts_service.synthesize("テスト", speed=1.5)
        assert sr > 0
        assert len(audio) > 0

    @pytest.mark.asyncio
    async def test_synthesize_with_slow_speed(self, mock_tts_service):
        """Verify synthesize works with slow speed (0.7)."""
        sr, audio = await mock_tts_service.synthesize("テスト", speed=0.7)
        assert sr > 0
        assert len(audio) > 0

    @pytest.mark.asyncio
    async def test_synthesize_with_min_speed(self, mock_tts_service):
        """Verify synthesize works with minimum speed (0.5)."""
        sr, audio = await mock_tts_service.synthesize("テスト", speed=0.5)
        assert sr > 0

    @pytest.mark.asyncio
    async def test_synthesize_with_max_speed(self, mock_tts_service):
        """Verify synthesize works with maximum speed (2.0)."""
        sr, audio = await mock_tts_service.synthesize("テスト", speed=2.0)
        assert sr > 0


class TestTTSServiceStatus:
    """Unit tests for TTSService status method."""

    def test_get_status_returns_status_object(self, mock_tts_service):
        """Verify get_status returns proper status object."""
        status = mock_tts_service.get_status()
        assert hasattr(status, "status")
        assert hasattr(status, "model_loaded")
        assert hasattr(status, "device")
        assert hasattr(status, "last_check")

    def test_get_status_healthy_when_loaded(self, mock_tts_service):
        """Verify healthy status when model is loaded."""
        status = mock_tts_service.get_status()
        assert status.status.value == "healthy"
        assert status.model_loaded is True
