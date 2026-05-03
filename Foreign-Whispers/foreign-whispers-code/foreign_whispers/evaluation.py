"""Clip-level alignment quality metrics.

Extracted from notebooks/foreign_whispers_pipeline.ipynb (M8-align).
Imports from foreign_whispers.alignment — no other dependencies.
"""
import statistics as _stats

from foreign_whispers.alignment import (
    AlignAction,
    AlignedSegment,
    SegmentMetrics,
    decide_action,
)


def clip_evaluation_report(
    metrics: list[SegmentMetrics],
    aligned: list[AlignedSegment],
) -> dict:
    """Return a summary dict of alignment quality metrics for one clip.

    Keys:
        mean_abs_duration_error_s: Mean |predicted_tts_s - source_duration_s| per segment.
        pct_severe_stretch: % of aligned segments with stretch_factor > 1.4.
        n_gap_shifts: Number of segments resolved via gap-shift.
        n_translation_retries: Number of segments that required re-ranking.
        total_cumulative_drift_s: End-to-end drift introduced by gap-shifts.
    """
    if not metrics:
        return {
            "mean_abs_duration_error_s": 0.0,
            "pct_severe_stretch":        0.0,
            "n_gap_shifts":              0,
            "n_translation_retries":     0,
            "total_cumulative_drift_s":  0.0,
        }

    errors    = [abs(m.predicted_tts_s - m.source_duration_s) for m in metrics]
    n_severe  = sum(1 for a in aligned if a.stretch_factor > 1.4)
    n_shifted = sum(1 for a in aligned if a.action == AlignAction.GAP_SHIFT)
    n_retry   = sum(1 for m in metrics if decide_action(m) == AlignAction.REQUEST_SHORTER)
    drift     = (
        aligned[-1].scheduled_end - aligned[-1].original_end
        if aligned else 0.0
    )

    return {
        "mean_abs_duration_error_s": round(_stats.mean(errors), 3),
        "pct_severe_stretch":        round(100 * n_severe / max(len(metrics), 1), 1),
        "n_gap_shifts":              n_shifted,
        "n_translation_retries":     n_retry,
        "total_cumulative_drift_s":  round(drift, 3),
    }



def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def dubbing_scorecard(
    metrics: list[SegmentMetrics],
    aligned_segments: list[AlignedSegment],
    align_report: dict,
) -> dict:
    """Return normalized dubbing quality scores in [0, 1].

    Higher is better. This scorecard focuses on dimensions available locally:
    timing accuracy, stretch quality, drift control, retry burden, and speaking
    rate naturalness.
    """
    if not metrics:
        return {
            "timing_accuracy": 1.0,
            "stretch_quality": 1.0,
            "drift_control": 1.0,
            "translation_fit": 1.0,
            "naturalness": 1.0,
            "overall": 1.0,
        }

    mean_err = float(align_report.get("mean_abs_duration_error_s", 0.0))
    pct_severe = float(align_report.get("pct_severe_stretch", 0.0))
    drift = abs(float(align_report.get("total_cumulative_drift_s", 0.0)))
    retries = float(align_report.get("n_translation_retries", 0.0))

    timing_accuracy = _clamp01(1.0 - (mean_err / 2.0))
    stretch_quality = _clamp01(1.0 - (pct_severe / 100.0))
    drift_control = _clamp01(1.0 - (drift / 5.0))
    translation_fit = _clamp01(1.0 - (retries / max(len(metrics), 1)))

    rates = []
    for m in metrics:
        if m.source_duration_s > 0:
            rates.append(m.tgt_char_count / m.source_duration_s)

    if len(rates) >= 2:
        mean_rate = _stats.mean(rates)
        rate_stdev = _stats.stdev(rates)
        cv = rate_stdev / mean_rate if mean_rate else 0.0
        naturalness = _clamp01(1.0 - cv)
    else:
        naturalness = 1.0

    overall = _stats.mean([
        timing_accuracy,
        stretch_quality,
        drift_control,
        translation_fit,
        naturalness,
    ])

    return {
        "timing_accuracy": round(timing_accuracy, 3),
        "stretch_quality": round(stretch_quality, 3),
        "drift_control": round(drift_control, 3),
        "translation_fit": round(translation_fit, 3),
        "naturalness": round(naturalness, 3),
        "overall": round(overall, 3),
    }
