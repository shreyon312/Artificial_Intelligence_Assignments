"""HTTP-agnostic service wrapping TTS engine functions."""

import json
import pathlib
from pathlib import Path
from typing import Any

from api.src.services.tts_engine import text_file_to_speech as tts_text_file_to_speech


class TTSService:
    """Thin wrapper around the TTS pipeline.

    Accepts *ui_dir* and a pre-loaded *tts_engine* via constructor injection.
    """

    def __init__(self, ui_dir: Path, tts_engine: Any) -> None:
        self.ui_dir = ui_dir
        self.tts_engine = tts_engine

    def text_file_to_speech(
        self,
        source_path: str,
        output_path: str,
        *,
        alignment: bool | None = None,
        speaker_voices: dict[str, str] | None = None,
        speaker_wav: str | None = None,
    ) -> None:
        tts_text_file_to_speech(source_path, output_path, self.tts_engine,
                            alignment=alignment, speaker_wav=speaker_wav)
        """Generate TTS audio from a translated JSON transcript.

        If speaker labels exist in the transcript, build a speaker-to-voice map
        so downstream TTS can select different reference voices per speaker.
        """
        speaker_voices = speaker_voices or {}

        source = Path(source_path)
        if source.exists():
            data = json.loads(source.read_text())
            speakers = sorted(
                {
                    seg.get("speaker")
                    for seg in data.get("segments", [])
                    if seg.get("speaker")
                }
            )

            for i, speaker in enumerate(speakers):
                speaker_voices.setdefault(speaker, f"speaker_{i}")

        tts_text_file_to_speech(
            source_path,
            output_path,
            self.tts_engine,
            alignment=alignment,
        )

    @staticmethod
    def title_for_video_id(video_id: str, search_dir: pathlib.Path) -> str | None:
        """Find a title by scanning *search_dir* for JSON files."""
        for f in search_dir.glob("*.json"):
            return f.stem
        return None

    def compute_alignment(
        self,
        en_transcript: dict,
        es_transcript: dict,
        silence_regions: list[dict],
        max_stretch: float = 1.4,
    ) -> list:
        """Run global alignment over EN and ES transcripts."""
        from foreign_whispers.alignment import compute_segment_metrics, global_align

        metrics = compute_segment_metrics(en_transcript, es_transcript)
        return global_align(metrics, silence_regions, max_stretch)