"""Outcome-blind temporal pairing for replicated HST dark cohorts."""

import math


def select_date_pairs(rows: list[dict], max_pairs: int = 3) -> list[list[dict]]:
    """Select the first compatible pair on each distinct UTC MJD day."""
    candidates = [r for r in rows if str(r["obs_id"]).lower().endswith("q")]
    candidates.sort(key=lambda r: (float(r["t_min"]), str(r["obs_id"])))
    used: set[int] = set()
    used_days: set[int] = set()
    pairs = []
    for index, first in enumerate(candidates):
        day = math.floor(float(first["t_min"]))
        if index in used or day in used_days:
            continue
        match = next(
            (
                (other_index, other)
                for other_index, other in enumerate(candidates[index + 1 :], index + 1)
                if other_index not in used
                and math.floor(float(other["t_min"])) == day
                and 0 < float(other["t_min"]) - float(first["t_min"]) <= 1
                and abs(float(other["t_exptime"]) / float(first["t_exptime"]) - 1) <= 0.01
            ),
            None,
        )
        if match is None:
            continue
        other_index, other = match
        pairs.append([first, other])
        used.update((index, other_index))
        used_days.add(day)
        if len(pairs) == max_pairs:
            break
    return pairs


def select_analysis_records(records: list[dict], role: str | None = None) -> list[dict]:
    """Filter a manifest while enforcing the sealed temporal-holdout boundary."""
    selected = [r for r in records if role is None or r.get("analysis_role") == role]
    if not selected:
        raise ValueError("No records selected")
    if any(r.get("analysis_role") == "temporal_holdout" for r in selected):
        raise ValueError("Refusing to open temporal-holdout FITS data")
    return selected
