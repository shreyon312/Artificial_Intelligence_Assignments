"""POST /api/tts/{video_id} — TTS with audio-sync endpoint."""

import asyncio
import functools
import json

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import FileResponse

from api.src.core.config import settings
from api.src.core.dependencies import resolve_title
from api.src.services.tts_service import TTSService
from foreign_whispers.voice_resolution import resolve_speaker_wav

router = APIRouter(prefix="/api")


async def _run_in_threadpool(executor, fn, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, functools.partial(fn, *args, **kwargs))


@router.post("/tts/{video_id}")
async def tts_endpoint(
    video_id: str,
    request: Request,
    config: str = Query(..., pattern=r"^c-[0-9a-f]{7}$"),
    alignment: bool = Query(False),
    speaker_wav: str = Query(None, description="Reference voice WAV path (e.g. 'es/default.wav')"),
):
    title = resolve_title(video_id)
    if title is None:
        raise HTTPException(status_code=404, detail=f"Video {video_id} not found in index")

    trans_dir = settings.translations_dir
    audio_dir = settings.tts_audio_dir / config
    audio_dir.mkdir(parents=True, exist_ok=True)

    wav_path = audio_dir / f"{title}.wav"
    source_path = trans_dir / f"{title}.json"

    if wav_path.exists():
        return {
            "video_id": video_id,
            "audio_path": str(wav_path),
            "config": config,
            "speaker_voices": {},
        }

    if not source_path.exists():
        raise HTTPException(status_code=404, detail=f"Translation file not found: {source_path}")

    if speaker_wav is None:
        speaker_wav = resolve_speaker_wav(settings.speakers_dir, "es")

    data = json.loads(source_path.read_text())
    speakers = sorted(
        {
            seg.get("speaker")
            for seg in data.get("segments", [])
            if seg.get("speaker")
        }
    )

    speaker_voices = {
        speaker: resolve_speaker_wav(settings.speakers_dir, "es", speaker)
        for speaker in speakers
    }

    svc = TTSService(
        ui_dir=settings.data_dir,
        tts_engine=None,
    )

    await _run_in_threadpool(
        None,
        svc.text_file_to_speech,
        str(source_path),
        str(audio_dir),
        alignment=alignment,
        speaker_voices=speaker_voices,
    )

    return {
        "video_id": video_id,
        "audio_path": str(wav_path),
        "config": config,
        "speaker_voices": speaker_voices,
    }


@router.get("/audio/{video_id}")
async def get_audio(
    video_id: str,
    config: str = Query(..., pattern=r"^c-[0-9a-f]{7}$"),
):
    title = resolve_title(video_id)
    if title is None:
        raise HTTPException(status_code=404, detail=f"Video {video_id} not found in index")

    audio_path = settings.tts_audio_dir / config / f"{title}.wav"
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(str(audio_path), media_type="audio/wav")