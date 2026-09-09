"""Preserve ACS engineering channels without inventing an active-sensor mapping."""

from pathlib import Path

from astropy.io import fits


def read_support(path: Path, expected_root: str) -> dict:
    """Read matched SPT values literally; missing strings remain explicit nulls."""
    with fits.open(path, memmap=False) as hdus:
        primary = hdus[0].header
        root = str(primary.get("ROOTNAME", "")).strip().lower()
        if root != expected_root.lower():
            raise ValueError("SPT root does not match exposure")
        header = hdus["UDL"].header
        if primary.get("INSTRUME") != "ACS" or header.get("DETECTOR") != "WFC":
            raise ValueError("Requires ACS/WFC support data")
        keys = ["JWDETMP1", "JWDETMP2", "READPATT", "JWROSPED", "CCDSETUP", "CCDAMP"]
        channels = {}
        for key in keys:
            value = header.get(key)
            if isinstance(value, str):
                value = value.strip()
                if value in {"", "--", "N/A"}:
                    value = None
            channels[key] = dict(
                value=value, comment=header.comments[key] if key in header else None
            )
    return dict(
        rootname=root,
        evidence="OBSERVED",
        channels=channels,
        operating_temperature_K=None,
        temperature_status="Both engineering channels retained; active-sensor mapping unverified",
        timing_status="Readout labels are not measured pixel dwell times",
    )
