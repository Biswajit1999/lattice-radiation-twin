"""Exploratory ACS paired-RAW trailing measurement, not a calibrated trap density."""

from pathlib import Path

import numpy as np
from astropy.io import fits
from scipy.ndimage import maximum_filter


def read_raw(path: Path, chip: int) -> tuple[np.ndarray, dict]:
    """Read full-frame RAW in native DN; crop using header offsets, orient away from register."""
    with fits.open(path, memmap=False) as hdus:
        primary = hdus[0].header
        if primary.get("INSTRUME") != "ACS" or primary.get("DETECTOR") != "WFC":
            raise ValueError("Requires ACS/WFC")
        if primary.get("SUBARRAY") or primary.get("IMAGETYP") != "DARK":
            raise ValueError("Requires a full-frame DARK")
        sci = next(h for h in hdus if h.name == "SCI" and h.header.get("CCDCHIP") == chip)
        header = sci.header
        if sci.data.shape != (2068, 4144) or header.get("BUNIT", "").strip() != "COUNTS":
            raise ValueError("Unsupported RAW geometry or units")
        x0, y0 = int(header["LTV1"]), int(header["LTV2"])
        if x0 != 24 or y0 not in {0, 20}:
            raise ValueError("Unexpected RAW science offset")
        image = sci.data[y0 : y0 + 2048, x0 : x0 + 4096].astype(np.float64)
        if chip == 1:
            image = image[::-1].copy()
        # Constant row offsets cancel in same-row local background estimates.
        # No gain conversion: the RAW calibrated ATODGAIN values may be zero.
        keys = [
            "ROOTNAME",
            "EXPSTART",
            "EXPTIME",
            "CCDGAIN",
            "CCDAMP",
            "CAL_VER",
            "OPUS_VER",
            "BIASFILE",
            "CCDTAB",
            "DARKFILE",
            "BSIDEOPS",
            "DATE-OBS",
        ]
        meta = {k: primary.get(k) for k in keys}
        meta.update(
            chip=chip,
            units="DN",
            evidence="OBSERVED",
            temperature_K=None,
            temperature_note="not present in primary RAW header; telemetry required",
            processing="RAW; local background only; no reference-bias/gain calibration",
            oriented_trail_direction="increasing array row",
            x0=x0,
            y0=y0,
        )
    return image, meta


def local_signal(image: np.ndarray) -> np.ndarray:
    """Same-row symmetric side pixels suppress row bias without mixing the trail column."""
    background = np.median(np.stack([np.roll(image, d, axis=1) for d in (-4, -3, 3, 4)]), axis=0)
    return image - background


def read_blv(path: Path, chip: int) -> tuple[np.ndarray, np.ndarray, dict]:
    """Read locally bias/gain-calibrated BLV and its initialized DQ array."""
    with fits.open(path, memmap=False) as hdus:
        h = hdus[0].header
        if h.get("BIASCORR") != "COMPLETE" or h.get("BLEVCORR") != "COMPLETE":
            raise ValueError("BLV requires completed bias/overscan calibration")
        if h.get("PCTECORR") != "OMIT" or h.get("DARKCORR") != "OMIT":
            raise ValueError("CTI and dark corrections must remain omitted for dark-trail analysis")
        sci = next(x for x in hdus if x.name == "SCI" and x.header.get("CCDCHIP") == chip)
        image = sci.data.astype(np.float64)
        dq = hdus["DQ", sci.header["EXTVER"]].data.astype(np.uint16)
        if image.shape != (2048, 4096) or sci.header["BUNIT"] != "ELECTRONS":
            raise ValueError("Unexpected calibrated geometry or units")
        if chip == 1:
            image, dq = image[::-1].copy(), dq[::-1].copy()
        keys = [
            "ROOTNAME",
            "EXPSTART",
            "EXPTIME",
            "CCDGAIN",
            "CCDAMP",
            "CAL_VER",
            "OPUS_VER",
            "BIASFILE",
            "CCDTAB",
            "DARKFILE",
            "BSIDEOPS",
            "DATE-OBS",
            "ATODGNA",
            "ATODGNB",
            "ATODGNC",
            "ATODGND",
        ]
        meta = {key: h.get(key) for key in keys}
        meta.update(
            chip=chip,
            units="electrons",
            evidence="OBSERVED",
            temperature_K=None,
            temperature_note="operating telemetry not yet reconstructed",
            processing="Official ACSCCD bias/gain/overscan calibrated BLV; no CTI correction",
        )
    return image, dq, meta


def dq_sample_mask(dqa: np.ndarray, dqb: np.ndarray) -> np.ndarray:
    """All used samples and their backgrounds must avoid non-hot/warm quality flags."""
    if dqa.shape != dqb.shape:
        raise ValueError("DQ shapes differ")
    bad = ((dqa | dqb) & (65535 ^ (16 | 64))) != 0
    return maximum_filter(bad, size=(11, 25), mode="constant", cval=1) == 0


def paired_trails(
    a: np.ndarray, b: np.ndarray, *, min_dn=100.0, max_dn=3000.0, length=5
) -> dict[str, np.ndarray]:
    """Persistent isolated peaks, downstream-minus-upstream trail, serial/blank controls.

    Both images must already point away from the parallel register in increasing row.
    Ratios are dimensionless in matched native-DN bins, not physical CTI per transfer.
    """
    if a.shape != b.shape or a.ndim != 2 or min(a.shape) < 32:
        raise ValueError("Matched 2-D frames of at least 32 pixels are required")
    if not (0 < min_dn < max_dn) or length < 1 or length > 10:
        raise ValueError("Invalid extraction configuration")
    sa, sb = local_signal(a), local_signal(b)
    mean = (sa + sb) / 2
    mask = (sa >= min_dn) & (sb >= min_dn) & (sa < max_dn) & (sb < max_dn)
    # Reject one-frame cosmic-ray impulses and unstable peaks.
    mask &= np.abs(sa - sb) <= 0.3 * np.maximum(mean, 1)
    mask &= (sa == maximum_filter(sa, size=3)) & (sb == maximum_filter(sb, size=3))
    margin = max(length + 2, 12)
    mask[:margin] = mask[-margin:] = False
    mask[:, :margin] = mask[:, -margin:] = False
    # Do not let side bands cross the amplifier boundary.
    middle = a.shape[1] // 2
    mask[:, middle - margin : middle + margin] = False
    y, x = np.where(mask)
    peak = mean[y, x]
    # Reject strong adjacent features in either image, excluding the central trail column.
    isolated = np.ones(len(y), dtype=bool)
    for dx in (-2, -1, 1, 2):
        for dy in range(-length, length + 1):
            isolated &= np.maximum(sa[y + dy, x + dx], sb[y + dy, x + dx]) < 0.2 * peak
    y, x, peak = y[isolated], x[isolated], peak[isolated]
    down = np.stack([mean[y + k, x] for k in range(1, length + 1)], axis=1)
    up = np.stack([mean[y - k, x] for k in range(1, length + 1)], axis=1)
    serial = sum(mean[y, x + k] - mean[y, x - k] for k in range(1, length + 1))
    blank = sum(mean[y + k, x + 8] - mean[y - k, x + 8] for k in range(1, length + 1))
    return dict(
        y=y,
        x=x,
        transfer=y + 1,
        peak_dn=peak,
        parallel_fraction=(down - up).sum(axis=1) / peak,
        leading_fraction=up.sum(axis=1) / peak,
        serial_fraction=serial / peak,
        blank_fraction=blank / peak,
        profile_fraction=(down - up) / peak[:, None],
    )


def summarize(values: np.ndarray, columns: np.ndarray, seed=271828, n_boot=400) -> dict:
    """Column-cluster bootstrap of the sample mean; excludes calibration systematics."""
    finite = np.isfinite(values)
    values, columns = values[finite], columns[finite]
    groups, inverse = np.unique(columns, return_inverse=True)
    if len(values) < 10 or len(groups) < 5:
        return dict(n=int(len(values)), n_columns=int(len(groups)), mean=None, lo=None, hi=None)
    totals = np.bincount(inverse, weights=values)
    counts = np.bincount(inverse)
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(groups), size=(n_boot, len(groups)))
    samples = totals[draws].sum(axis=1) / counts[draws].sum(axis=1)
    lo, hi = np.quantile(samples, [0.025, 0.975])
    return dict(
        n=int(len(values)),
        n_columns=int(len(groups)),
        mean=float(values.mean()),
        lo=float(lo),
        hi=float(hi),
    )
