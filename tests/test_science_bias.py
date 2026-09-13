import numpy as np
import pytest

from lattice.euclid_transfer import release_kernel
from lattice.science_bias import (
    aperture_moments,
    apply_parallel_trail,
    elliptic_covariance,
    forced_response_metrics,
    gaussian_source,
    weighted_aperture_moments,
)


def test_gaussian_source_and_trail_conserve_flux_with_overflow():
    image = gaussian_source((96, 96), (48, 24), 1000, np.eye(2))
    kernel = release_kernel(0.020, 0.00402, 4096)
    trailed, overflow = apply_parallel_trail(image, kernel, 0.01, 1.0)
    assert abs(trailed.sum() + overflow - image.sum()) / image.sum() < 1e-12
    assert np.all(trailed >= 0)


def test_zero_capture_is_identity_and_moments_are_finite():
    covariance = elliptic_covariance(2, 0.7, 0.3, 0.7)
    image = gaussian_source((96, 96), (48, 24), 3000, covariance)
    kernel = release_kernel(0.020, 0.00402, 4096)
    trailed, overflow = apply_parallel_trail(image, kernel, 0, 1)
    assert np.array_equal(trailed, image)
    assert overflow == 0
    measured = aperture_moments(image + 20, 20, (48, 24), 12)
    assert measured is not None
    assert np.isfinite([measured.e1, measured.e2, measured.size_trace]).all()


def test_parallel_trail_moves_centroid_only_downstream():
    image = gaussian_source((96, 96), (48, 24), 10_000, np.eye(2))
    kernel = release_kernel(0.020, 0.00402, 4096)
    trailed, _ = apply_parallel_trail(image, kernel, 0.01, 1)
    clean = aperture_moments(image, 0, (48, 24), 12)
    damaged = aperture_moments(trailed, 0, (48, 24), 12)
    assert clean is not None and damaged is not None
    assert abs(damaged.x - clean.x) < 1e-12
    assert damaged.y > clean.y


def test_weighted_moments_recover_symmetric_source_center():
    source = gaussian_source((41, 41), (20.0, 15.0), 1000, np.eye(2) * 2.0**2)
    measured = weighted_aperture_moments(source + 20, 20, (20.0, 15.0), 12, 3.0)
    assert measured is not None
    assert measured.x == pytest.approx(20.0, abs=1e-12)
    assert measured.y == pytest.approx(15.0, abs=1e-12)
    assert measured.e1 == pytest.approx(0.0, abs=1e-12)
    assert measured.e2 == pytest.approx(0.0, abs=1e-12)


def test_weighted_moments_reject_nonpositive_sigma():
    with pytest.raises(ValueError, match="weight_sigma"):
        weighted_aperture_moments(np.ones((5, 5)), 0, (2, 2), 2, 0)


def test_forced_response_is_zero_for_identical_pair():
    source = gaussian_source((41, 41), (20.0, 15.0), 1000, np.eye(2) * 2.0**2)
    metrics = forced_response_metrics(source + 20, source + 20, source, 20, (20, 15), 12, 3)
    assert max(abs(value) for value in metrics.values()) == 0


def test_forced_response_detects_downstream_trail():
    source = gaussian_source((41, 41), (20.0, 15.0), 1000, np.eye(2) * 2.0**2)
    kernel = release_kernel(0.020, 0.00402, 4096)
    damaged, _ = apply_parallel_trail(source, kernel, 0.01, 1)
    metrics = forced_response_metrics(source, damaged, source, 0, (20, 15), 12, 3)
    assert abs(metrics["centroid_x_pixels"]) < 1e-12
    assert metrics["centroid_y_pixels"] > 0
