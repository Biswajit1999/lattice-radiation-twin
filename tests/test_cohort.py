from lattice.cohort import select_date_pairs


def row(obs_id, time, exposure=1000):
    return {"obs_id": obs_id, "t_min": str(time), "t_exptime": str(exposure)}


def test_pairs_are_deterministic_distinct_days_and_duration_matched():
    rows = [
        row("not_an_individual", 10.01),
        row("aQ", 10.02),
        row("bq", 10.03, 1100),
        row("cq", 10.04),
        row("dq", 10.05),
        row("eq", 11.01),
        row("fq", 11.02),
        row("gq", 12.01),
        row("hq", 12.02),
        row("iq", 13.01),
        row("jq", 13.02),
    ]
    pairs = select_date_pairs(list(reversed(rows)), max_pairs=3)
    assert [[r["obs_id"] for r in pair] for pair in pairs] == [
        ["aQ", "cq"],
        ["eq", "fq"],
        ["gq", "hq"],
    ]
