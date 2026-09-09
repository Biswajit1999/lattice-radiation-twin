import hashlib
import io

import pytest

from lattice.provenance import fetch, validate_record, verify


@pytest.fixture
def spec():
    return dict(
        source_identifier="test:archive",
        mission="HST",
        instrument="ACS/WFC",
        original_filename="test.fits",
        tier="A",
        url="https://example.org/test.fits",
        processing_level="mock",
        pipeline_version="mock-v1",
        usage_note="test only",
        selection_reason="mock download fixture, not mission data",
    )


def opener(payload, declared=None):
    def open_mock(request, timeout):
        result = io.BytesIO(payload)
        result.headers = {"Content-Length": str(len(payload) if declared is None else declared)}
        return result

    return open_mock


def test_download_and_tamper_detection(tmp_path, spec):
    payload = b"deterministic mock archive"
    record = fetch(spec, tmp_path, "a" * 40, opener=opener(payload))
    assert record["sha256"] == hashlib.sha256(payload).hexdigest()
    path = verify(record, tmp_path)
    again = fetch(
        spec, tmp_path, "a" * 40, expected_sha256=record["sha256"], opener=opener(payload)
    )
    assert again["cache_path"] == record["cache_path"]
    path.write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="mismatch"):
        verify(record, tmp_path)


@pytest.mark.parametrize("kind", ["oversize", "truncated", "checksum", "empty"])
def test_invalid_downloads(tmp_path, spec, kind):
    kwargs = dict(opener=opener(b"abc"))
    if kind == "oversize":
        kwargs["max_bytes"] = 2
    elif kind == "truncated":
        kwargs["opener"] = opener(b"abc", declared=10)
    elif kind == "empty":
        kwargs["opener"] = opener(b"")
    else:
        kwargs["expected_sha256"] = "0" * 64
    with pytest.raises(ValueError):
        fetch(spec, tmp_path, "a" * 40, **kwargs)
    assert not list(tmp_path.rglob("*.part"))


def test_contract_rejects_missing_fields():
    with pytest.raises(ValueError, match="Missing"):
        validate_record({})


def test_path_escape(tmp_path, spec):
    spec["original_filename"] = "../secret"
    with pytest.raises(ValueError, match="Unsafe"):
        fetch(spec, tmp_path, "a" * 40)
