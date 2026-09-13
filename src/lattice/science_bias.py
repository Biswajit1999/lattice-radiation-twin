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


def weighted_aperture_moments(
    image: np.ndarray,
    background: float,
    center: tuple[float, float],
    radius: float,
    weight_sigma: float,
) -> Moments | None:
    """Measure fixed-centre Gaussian-weighted moments inside an aperture."""
    if weight_sigma <= 0:
        raise ValueError("weight_sigma must be positive")
    y, x = np.indices(image.shape, dtype=float)
    radius_squared = (x - center[0]) ** 2 + (y - center[1]) ** 2
    aperture = radius_squared <= radius**2
    weight = np.exp(-0.5 * radius_squared / weight_sigma**2)
    signal = np.where(aperture, weight * (image - background), 0.0)
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


def forced_response_metrics(
    clean: np.ndarray,
    damaged: np.ndarray,
    reference: np.ndarray,
    background: float,
    center: tuple[float, float],
    radius: float,
    weight_sigma: float,
) -> dict[str, float]:
    """Return fixed-template linearized responses for a paired image."""
    if clean.shape != damaged.shape or clean.shape != reference.shape:
        raise ValueError("clean, damaged, and reference shapes must match")
    if weight_sigma <= 0:
        raise ValueError("weight_sigma must be positive")
    y, x = np.indices(clean.shape, dtype=float)
    dx = x - center[0]
    dy = y - center[1]
    radius_squared = dx**2 + dy**2
    weight = np.where(
        radius_squared <= radius**2,
        np.exp(-0.5 * radius_squared / weight_sigma**2),
        0.0,
    )

    def sums(image: np.ndarray, level: float) -> np.ndarray:
        signal = weight * (image - level)
        return np.array(
            [
                signal.sum(),
                np.sum(signal * dx),
                np.sum(signal * dy),
                np.sum(signal * dx**2),
                np.sum(signal * dy**2),
                np.sum(signal * dx * dy),
            ],
            dtype=float,
        )

    ref = sums(reference, 0.0)
    reference_flux = ref[0]
    reference_trace = ref[3] + ref[4]
    if reference_flux <= 0 or reference_trace <= 0 or not np.isfinite(ref).all():
        raise ValueError("reference must have positive finite weighted flux and trace")
    delta = sums(damaged, background) - sums(clean, background)
    reference_e1 = (ref[3] - ref[4]) / reference_trace
    reference_e2 = 2 * ref[5] / reference_trace
    delta_trace = delta[3] + delta[4]
    return {
        "flux_fraction": float(delta[0] / reference_flux),
        "centroid_x_pixels": float(delta[1] / reference_flux),
        "centroid_y_pixels": float(delta[2] / reference_flux),
        "centroid_y_mas": float(100 * delta[2] / reference_flux),
        "e1": float((delta[3] - delta[4] - reference_e1 * delta_trace) / reference_trace),
        "e2": float((2 * delta[5] - reference_e2 * delta_trace) / reference_trace),
        "size_fraction": float(delta_trace / reference_trace),
    }


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
