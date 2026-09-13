import numpy as np

from lattice.euclid_transfer import release_kernel
from lattice.science_bias import (
    aperture_moments,
    apply_parallel_trail,
    elliptic_covariance,
    gaussian_source,
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
