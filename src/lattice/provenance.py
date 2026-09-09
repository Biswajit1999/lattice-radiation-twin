"""Content-verified downloads. No mission data are bundled with this module."""

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse
from urllib.request import Request, urlopen

FIELDS = {
    "source_identifier",
    "mission",
    "instrument",
    "retrieved_at",
    "original_filename",
    "size_bytes",
    "sha256",
    "processing_level",
    "pipeline_version",
    "usage_note",
    "software_commit",
    "selection_reason",
    "tier",
    "url",
    "cache_path",
}


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def validate_record(record: dict) -> None:
    if not FIELDS <= record.keys():
        raise ValueError(f"Missing provenance fields: {FIELDS - record.keys()}")
    if any(
        not isinstance(record[k], str) or not record[k].strip() for k in FIELDS - {"size_bytes"}
    ):
        raise ValueError("Provenance strings must be nonempty; use explicit unknown where needed")
    if not isinstance(record["size_bytes"], int) or record["size_bytes"] <= 0:
        raise ValueError("Invalid object size")
    if not re.fullmatch(r"[0-9a-f]{64}", record["sha256"]):
        raise ValueError("Invalid SHA-256")
    if not re.fullmatch(r"[0-9a-f]{40}", record["software_commit"]):
        raise ValueError("A full software commit is required")
    if record["tier"] not in {"A", "B"}:
        raise ValueError("Downloaded real data must be Tier A or B")
    stamp = datetime.fromisoformat(record["retrieved_at"])
    if stamp.tzinfo is None or stamp.utcoffset().total_seconds() != 0:
        raise ValueError("Retrieval time must be timezone-aware UTC")
    if Path(record["original_filename"]).name != record["original_filename"]:
        raise ValueError("Filename must not contain a path")


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    with NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        stream.write(text)
        temp = Path(stream.name)
    temp.replace(path)


def verify(record: dict, root: Path) -> Path:
    validate_record(record)
    path = (root / record["cache_path"]).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Cache path escapes repository")
    if path.stat().st_size != record["size_bytes"] or sha256(path) != record["sha256"]:
        raise ValueError(f"Provenance mismatch: {path.name}")
    return path


def register(path: Path, spec: dict, root: Path, commit: str) -> dict:
    record = dict(spec)
    record.update(
        retrieved_at=datetime.now(UTC).isoformat(),
        size_bytes=path.stat().st_size,
        sha256=sha256(path),
        software_commit=commit,
        cache_path=path.resolve().relative_to(root.resolve()).as_posix(),
    )
    record.setdefault("pipeline_version", "unknown: not supplied by archive")
    source_dir = Path(__file__).parent
    record["acquisition_source_sha256"] = {
        p.name: sha256(p) for p in sorted(source_dir.glob("*.py"))
    }
    validate_record(record)
    return record


def fetch(
    spec: dict,
    root: Path,
    commit: str,
    max_bytes: int = 200_000_000,
    expected_sha256: str | None = None,
    opener=urlopen,
) -> dict:
    """Atomic download with size bound; pinned replay rejects changed upstream bytes."""
    if urlparse(spec["url"]).scheme != "https":
        raise ValueError("Remote downloads require HTTPS")
    name = spec["original_filename"]
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", name) or name in {".", ".."}:
        raise ValueError("Unsafe original filename")
    cache = root / "data/cache" / spec["mission"].lower()
    if not cache.resolve().is_relative_to((root / "data/cache").resolve()):
        raise ValueError("Invalid mission path")
    cache.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        request = Request(spec["url"], headers={"User-Agent": "LATTICE-research/0.1"})
        with opener(request, timeout=60) as response:
            declared = response.headers.get("Content-Length")
            if declared and int(declared) > max_bytes:
                raise ValueError("Object exceeds download budget")
            with NamedTemporaryFile(dir=cache, delete=False, suffix=".part") as stream:
                temp = Path(stream.name)
                total = 0
                while block := response.read(1024 * 1024):
                    total += len(block)
                    if total > max_bytes:
                        raise ValueError("Object exceeds download budget")
                    stream.write(block)
            if declared and total != int(declared):
                raise ValueError("Truncated download")
        digest = sha256(temp)
        if expected_sha256 and digest != expected_sha256:
            raise ValueError("Upstream bytes changed: pinned checksum mismatch")
        destination = cache / digest / name
        destination.parent.mkdir(exist_ok=True)
        temp.replace(destination)
        return register(destination, spec, root, commit)
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)
