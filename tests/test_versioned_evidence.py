"""CI checks literal archival metadata bytes even without the large FITS cache."""

import json
from pathlib import Path

from lattice.provenance import verify


def test_versioned_archive_snapshots_match_manifest_bytes():
    root = Path(__file__).resolve().parents[1]
    checked = 0
    for manifest in (root / "data/manifests").glob("*.json"):
        records = json.loads(manifest.read_text())
        if not isinstance(records, list):
            continue
        for record in records:
            if isinstance(record, dict) and record.get("cache_path", "").startswith(
                "data/metadata/"
            ):
                verify(record, root)
                checked += 1
    assert checked >= 1
