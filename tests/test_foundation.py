import tomllib
from pathlib import Path


def test_required_contracts_exist():
    root = Path(__file__).resolve().parents[1]
    for filename in (
        "PROJECT_STATE.md",
        "docs/BUILD_LEDGER.md",
        "docs/NOVELTY_AUDIT.md",
        "docs/DATA_CONTRACT.md",
        "docs/VALIDATION_CONTRACT.md",
    ):
        assert (root / filename).read_text(encoding="utf-8").strip()
    config = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    assert config["project"]["authors"] == [{"name": "Biswajit Jana"}]
