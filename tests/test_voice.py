import pytest

from app.services.voice import DEFAULT_TTS_PITCH, DEFAULT_TTS_RATE, DEFAULT_TTS_VOICE, text_to_speech_ogg


@pytest.mark.asyncio
async def test_text_to_speech_creates_audio_file():
    path = await text_to_speech_ogg("Я рядом.")
    try:
        assert path.exists()
        assert path.stat().st_size > 1000
    finally:
        path.unlink(missing_ok=True)


def test_default_tts_voice_is_softer_female_voice():
    assert DEFAULT_TTS_VOICE == "ru-RU-SvetlanaNeural"
    assert DEFAULT_TTS_RATE == "-12%"
    assert DEFAULT_TTS_PITCH == "-6Hz"
