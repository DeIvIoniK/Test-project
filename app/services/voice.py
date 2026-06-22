import asyncio
import tempfile
from pathlib import Path

import edge_tts
from aiogram import Bot
from aiogram.types import Voice
from faster_whisper import WhisperModel

_MODEL: WhisperModel | None = None
DEFAULT_TTS_VOICE = "ru-RU-SvetlanaNeural"
DEFAULT_TTS_RATE = "-12%"
DEFAULT_TTS_PITCH = "-6Hz"


def _get_model() -> WhisperModel:
    global _MODEL
    if _MODEL is None:
        _MODEL = WhisperModel("small", device="cpu", compute_type="int8")
    return _MODEL


def _transcribe_sync(path: str) -> str:
    segments, _info = _get_model().transcribe(path, language="ru", vad_filter=True)
    return " ".join(segment.text.strip() for segment in segments).strip()


async def transcribe_telegram_voice(bot: Bot, voice: Voice) -> str | None:
    with tempfile.TemporaryDirectory() as tmpdir:
        ogg_path = Path(tmpdir) / "voice.ogg"
        file = await bot.get_file(voice.file_id)
        await bot.download_file(file.file_path, destination=ogg_path)
        text = await asyncio.to_thread(_transcribe_sync, str(ogg_path))
        return text or None


async def text_to_speech_ogg(
    text: str,
    voice: str = DEFAULT_TTS_VOICE,
    rate: str = DEFAULT_TTS_RATE,
    pitch: str = DEFAULT_TTS_PITCH,
) -> Path:
    tmp = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
    tmp.close()
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
    await communicate.save(tmp.name)
    return Path(tmp.name)
