"""Conditional image-domain measurements for a verified linear CTI kernel."""

from dataclasses import dataclass

import numpy as np

from lattice.euclid_transfer import ReleaseKernel


@dataclass(frozen=True)
class Moments:
    flux: float
    x: float
    y: float
    qxx: float
    qyy: float
    qxy: float

    @property
    def e1(self) -> float:
        return (self.qxx - self.qyy) / (self.qxx + self.qyy)

    @property
    def e2(self) -> float:
        return 2 * self.qxy / (self.qxx + self.qyy)

    @property
    def size_trace(self) -> float:
        return self.qxx + self.qyy


def gaussian_source(
    shape: tuple[int, int],
    center: tuple[float, float],
    flux: float,
    covariance: np.ndarray,
) -> np.ndarray:
    if flux <= 0 or covariance.shape != (2, 2):
        raise ValueError("positive flux and a 2x2 covariance are required")
    y, x = np.indices(shape, dtype=float)
    delta = np.stack((x - center[0], y - center[1]), axis=-1)
    inverse = np.linalg.inv(covariance)
    radius = np.einsum("...i,ij,...j->...", delta, inverse, delta)
    image = np.exp(-0.5 * radius)
    return image * (flux / image.sum())


def apply_parallel_trail(
    image: np.ndarray,
    kernel: ReleaseKernel,
    full_array_captured_fraction: float,
    transfer_distance_fraction: float,
) -> tuple[np.ndarray, float]:
    if image.ndim != 2 or np.any(image < 0):
        raise ValueError("image must be a non-negative 2D array")
    effective = full_array_captured_fraction * transfer_distance_fraction
    if not 0 <= effective <= 1:
        raise ValueError("effective captured fraction must lie in [0, 1]")
    height = image.shape[0]
    response = np.concatenate(([1 - effective], effective * kernel.probability[:height]))
    output = np.empty_like(image, dtype=float)
    overflow = 0.0
    for column in range(image.shape[1]):
        full = np.convolve(image[:, column], response, mode="full")
        output[:, column] = full[:height]
        overflow += float(full[height:].sum())
    represented_release = float(kernel.probability[:height].sum())
    omitted_kernel_mass = max(0.0, 1 - represented_release)
    overflow += float(image.sum() * effective * omitted_kernel_mass)
    return output, overflow


def aperture_moments(
    image: np.ndarray,
    background: float,
    center: tuple[float, float],
    radius: float,
) -> Moments | None:
    y, x = np.indices(image.shape, dtype=float)
    aperture = (x - center[0]) ** 2 + (y - center[1]) ** 2 <= radius**2
    signal = np.where(aperture, image - background, 0.0)
    flux = float(signal.sum())
    if not np.isfinite(flux) or flux <= 0:
        return None
    xbar = float(np.sum(signal * x) / flux)
    ybar = float(np.sum(signal * y) / flux)
    qxx = float(np.sum(signal * (x - xbar) ** 2) / flux)
    qyy = float(np.sum(signal * (y - ybar) ** 2) / flux)
    qxy = float(np.sum(signal * (x - xbar) * (y - ybar)) / flux)
    if not np.all(np.isfinite([xbar, ybar, qxx, qyy, qxy])) or qxx + qyy <= 0:
        return None
    return Moments(flux, xbar, ybar, qxx, qyy, qxy)


def elliptic_covariance(
    sigma_major: float,
    axis_ratio: float,
    angle_radians: float,
    psf_sigma: float,
    g1: float = 0.0,
    g2: float = 0.0,
) -> np.ndarray:
    rotation = np.array(
        [
            [np.cos(angle_radians), -np.sin(angle_radians)],
            [np.sin(angle_radians), np.cos(angle_radians)],
        ]
    )
    intrinsic = rotation @ np.diag([sigma_major**2, (sigma_major * axis_ratio) ** 2]) @ rotation.T
    shear = np.array([[1 + g1, g2], [g2, 1 - g1]])
    return shear @ intrinsic @ shear.T + np.eye(2) * psf_sigma**2
