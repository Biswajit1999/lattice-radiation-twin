import numpy as np
import pytest
from astropy.io import fits

from lattice.hst import paired_trails, read_raw, summarize


def inject(fraction=0.04, seed=17):
    rng = np.random.default_rng(seed)
    a = rng.normal(1000, 0.05, (160, 160))
    b = rng.normal(1100, 0.05, (160, 160))
    weights = np.exp(-np.arange(1, 6) / 2)
    weights /= weights.sum()
    for y, x in [(30, 30), (60, 40), (100, 110), (125, 125)]:
        a[y, x] += 500
        b[y, x] += 500
        a[y + 1 : y + 6, x] += 500 * fraction * weights
        b[y + 1 : y + 6, x] += 500 * fraction * weights
    return a, b


def test_known_trail_and_blank_controls():
    result = paired_trails(*inject())
    assert len(result["x"]) == 4
    assert np.mean(result["parallel_fraction"]) == pytest.approx(0.04, abs=0.001)
    assert abs(np.mean(result["blank_fraction"])) < 0.001
    assert abs(np.mean(result["serial_fraction"])) < 0.001


def test_zero_trail_and_reversed_direction():
    assert abs(np.mean(paired_trails(*inject(0))["parallel_fraction"])) < 0.001
    a, b = inject()
    reverse = paired_trails(a[::-1], b[::-1])
    assert np.mean(reverse["parallel_fraction"]) == pytest.approx(-0.04, abs=0.001)


def test_single_frame_cosmic_ray_rejected():
    a, b = inject()
    a[80, 30] += 1000
    assert len(paired_trails(a, b)["x"]) == 4


def test_bootstrap_seed_and_empty():
    assert summarize(np.array([]), np.array([]))["mean"] is None
    a = np.arange(100.0)
    assert summarize(a, a % 10) == summarize(a, a % 10)
    simultaneous = summarize(a, a % 10, n_boot=20_000, alpha=0.05 / 32)
    assert simultaneous["alpha"] == pytest.approx(0.05 / 32)
    assert simultaneous["lo"] <= simultaneous["mean"] <= simultaneous["hi"]
    with pytest.raises(ValueError, match="alpha"):
        summarize(a, a % 10, alpha=0)


def test_raw_geometry_and_orientation(tmp_path):
    # Compact compressed-in-memory pattern, written only into a temporary test file.
    header = fits.Header(dict(INSTRUME="ACS", DETECTOR="WFC", SUBARRAY=False, IMAGETYP="DARK"))
    raw = np.zeros((2068, 4144), dtype=np.uint16)
    raw[20 + 10, 24 + 50] = 999
    sci = fits.ImageHDU(raw, name="SCI")
    sci.header.update(CCDCHIP=1, LTV1=24, LTV2=20, BUNIT="COUNTS")
    path = tmp_path / "mock_raw.fits"
    fits.HDUList([fits.PrimaryHDU(header=header), sci]).writeto(path)
    image, metadata = read_raw(path, 1)
    assert image.shape == (2048, 4096)
    assert image[2047 - 10, 50] == 999
    assert metadata["temperature_K"] is None
