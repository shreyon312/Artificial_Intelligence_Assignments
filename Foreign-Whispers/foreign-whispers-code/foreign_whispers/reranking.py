"""Deterministic failure analysis and translation re-ranking stubs.

The failure analysis function uses simple threshold rules derived from
SegmentMetrics.  The translation re-ranking function is a **student assignment**
— see the docstring for inputs, outputs, and implementation guidance.
"""

import dataclasses
import logging

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class TranslationCandidate:
    """A candidate translation that fits a duration budget.

    Attributes:
        text: The translated text.
        char_count: Number of characters in *text*.
        brevity_rationale: Short explanation of what was shortened.
    """
    text: str
    char_count: int
    brevity_rationale: str = ""


@dataclasses.dataclass
class FailureAnalysis:
    """Diagnostic summary of the dominant failure mode in a clip.

    Attributes:
        failure_category: One of "duration_overflow", "cumulative_drift",
            "stretch_quality", or "ok".
        likely_root_cause: One-sentence description.
        suggested_change: Most impactful next action.
    """
    failure_category: str
    likely_root_cause: str
    suggested_change: str


def analyze_failures(report: dict) -> FailureAnalysis:
    """Classify the dominant failure mode from a clip evaluation report.

    Pure heuristic — no LLM needed.  The thresholds below match the policy
    bands defined in ``alignment.decide_action``.

    Args:
        report: Dict returned by ``clip_evaluation_report()``.  Expected keys:
            ``mean_abs_duration_error_s``, ``pct_severe_stretch``,
            ``total_cumulative_drift_s``, ``n_translation_retries``.

    Returns:
        A ``FailureAnalysis`` dataclass.
    """
    mean_err = report.get("mean_abs_duration_error_s", 0.0)
    pct_severe = report.get("pct_severe_stretch", 0.0)
    drift = abs(report.get("total_cumulative_drift_s", 0.0))
    retries = report.get("n_translation_retries", 0)

    if pct_severe > 20:
        return FailureAnalysis(
            failure_category="duration_overflow",
            likely_root_cause=(
                f"{pct_severe:.0f}% of segments exceed the 1.4x stretch threshold — "
                "translated text is consistently too long for the available time window."
            ),
            suggested_change="Implement duration-aware translation re-ranking (P8).",
        )

    if drift > 3.0:
        return FailureAnalysis(
            failure_category="cumulative_drift",
            likely_root_cause=(
                f"Total drift is {drift:.1f}s — small per-segment overflows "
                "accumulate because gaps between segments are not being reclaimed."
            ),
            suggested_change="Enable gap_shift in the global alignment optimizer (P9).",
        )

    if mean_err > 0.8:
        return FailureAnalysis(
            failure_category="stretch_quality",
            likely_root_cause=(
                f"Mean duration error is {mean_err:.2f}s — segments fit within "
                "stretch limits but the stretch distorts audio quality."
            ),
            suggested_change="Lower the mild_stretch ceiling or shorten translations.",
        )

    return FailureAnalysis(
        failure_category="ok",
        likely_root_cause="No dominant failure mode detected.",
        suggested_change="Review individual outlier segments if any remain.",
    )

def get_shorter_translations(
    source_text: str,
    baseline_es: str,
    target_duration_s: float,
    context_prev: str = "",
    context_next: str = "",
) -> list[TranslationCandidate]:
    """Return shorter translation candidates that fit *target_duration_s*."""

    max_chars = max(1, int(target_duration_s * 15))
    text = " ".join(baseline_es.strip().split())

    replacements = [
        ("en este momento", "ahora"),
        ("en este preciso momento", "ahora"),
        ("en la actualidad", "ahora"),
        ("por supuesto", "claro"),
        ("sin embargo", "pero"),
        ("por lo tanto", "así que"),
        ("debido a que", "porque"),
        ("con el fin de", "para"),
        ("a causa de", "por"),
        ("tener que", "deber"),
        ("vamos a", "vamos"),
        ("usted", "tú"),
        ("realmente", ""),
        ("básicamente", ""),
        ("simplemente", ""),
        ("absolutamente", ""),
        ("muy ", ""),
    ]

    candidates = []

    def add_candidate(candidate_text: str, rationale: str):
        candidate_text = " ".join(candidate_text.strip().split())
        if not candidate_text:
            return
        if candidate_text == baseline_es.strip():
            return
        if len(candidate_text) <= len(baseline_es.strip()):
            candidates.append(
                TranslationCandidate(
                    text=candidate_text,
                    char_count=len(candidate_text),
                    brevity_rationale=rationale,
                )
            )

    # Candidate 1: phrase/synonym compression
    compressed = text
    changed = []
    lower_text = compressed.lower()

    for old, new in replacements:
        if old in lower_text:
            compressed = compressed.replace(old, new)
            compressed = compressed.replace(old.capitalize(), new.capitalize())
            changed.append(f"{old} → {new or 'removed'}")
            lower_text = compressed.lower()

    add_candidate(
        compressed,
        "Applied common Spanish phrase shortening: " + ", ".join(changed)
        if changed
        else "Normalized whitespace and removed avoidable filler.",
    )

    # Candidate 2: remove parenthetical or after-dash clauses
    for sep in [" — ", " - ", ": ", "; "]:
        if sep in compressed:
            add_candidate(
                compressed.split(sep)[0],
                f"Kept main clause before '{sep.strip()}'.",
            )

    # Candidate 3: trim trailing filler after commas
    if "," in compressed:
        parts = [p.strip() for p in compressed.split(",") if p.strip()]
        if parts:
            shortened = parts[0]
            if len(shortened) >= max_chars * 0.5:
                add_candidate(shortened, "Kept the main clause before comma.")

    # Candidate 4: if still too long, preserve as many words as fit
    words = compressed.split()
    trimmed_words = []
    for word in words:
        test = " ".join(trimmed_words + [word])
        if len(test) <= max_chars:
            trimmed_words.append(word)
        else:
            break

    if trimmed_words:
        trimmed = " ".join(trimmed_words)
        if len(trimmed_words) < len(words):
            add_candidate(
                trimmed,
                f"Trimmed to fit the ~{max_chars}-character duration budget.",
            )

    # Remove duplicates
    unique = {}
    for c in candidates:
        unique[c.text] = c

    # Prefer candidates that fit budget, then shortest first
    sorted_candidates = sorted(
        unique.values(),
        key=lambda c: (len(c.text) > max_chars, c.char_count),
    )

    return sorted_candidates
