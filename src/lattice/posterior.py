"""Posterior samplers and chain diagnostics used by LATTICE."""

from collections.abc import Callable

import numpy as np
from scipy.stats import norm, rankdata


def elliptical_slice_step(
    current: np.ndarray,
    current_log_likelihood: float,
    prior_mean: np.ndarray,
    prior_sd: np.ndarray,
    log_likelihood: Callable[[np.ndarray], float],
    rng: np.random.Generator,
    max_contractions: int = 1000,
) -> tuple[np.ndarray, float, int]:
    """Take one elliptical-slice step for an independent Gaussian prior."""
    centered = np.asarray(current, dtype=float) - prior_mean
    auxiliary = rng.normal(0.0, prior_sd)
    threshold = current_log_likelihood + np.log(rng.random())
    angle = rng.uniform(0.0, 2 * np.pi)
    angle_min = angle - 2 * np.pi
    angle_max = angle
    for contractions in range(max_contractions + 1):
        proposal = prior_mean + centered * np.cos(angle) + auxiliary * np.sin(angle)
        proposal_log_likelihood = float(log_likelihood(proposal))
        if np.isfinite(proposal_log_likelihood) and proposal_log_likelihood >= threshold:
            return proposal, proposal_log_likelihood, contractions
        if angle < 0:
            angle_min = angle
        else:
            angle_max = angle
        angle = rng.uniform(angle_min, angle_max)
    raise RuntimeError(f"Elliptical slice exceeded {max_contractions} contractions")


def sample_elliptical_slice(
    log_likelihood: Callable[[np.ndarray], float],
    prior_mean: np.ndarray,
    prior_sd: np.ndarray,
    seed: int,
    burn_in: int,
    draws: int,
) -> dict:
    """Draw a deterministic-seed ESS chain from likelihood times Gaussian prior."""
    if burn_in < 0 or draws < 1:
        raise ValueError("burn_in must be non-negative and draws must be positive")
    prior_mean = np.asarray(prior_mean, dtype=float)
    prior_sd = np.asarray(prior_sd, dtype=float)
    if prior_mean.shape != prior_sd.shape or np.any(prior_sd <= 0):
        raise ValueError("Prior mean and positive standard deviation must share a shape")
    rng = np.random.default_rng(seed)
    current = rng.normal(prior_mean, prior_sd)
    current_log_likelihood = float(log_likelihood(current))
    if not np.isfinite(current_log_likelihood):
        current = prior_mean.copy()
        current_log_likelihood = float(log_likelihood(current))
    if not np.isfinite(current_log_likelihood):
        raise ValueError("No finite likelihood at the prior draw or prior mean")
    samples = np.empty((draws, len(prior_mean)))
    contractions = np.empty(burn_in + draws, dtype=int)
    likelihoods = np.empty(draws)
    for index in range(burn_in + draws):
        current, current_log_likelihood, contractions[index] = elliptical_slice_step(
            current,
            current_log_likelihood,
            prior_mean,
            prior_sd,
            log_likelihood,
            rng,
        )
        if index >= burn_in:
            retained = index - burn_in
            samples[retained] = current
            likelihoods[retained] = current_log_likelihood
    return {
        "draws": samples,
        "log_likelihood": likelihoods,
        "contractions": contractions,
    }


def sample_random_walk_metropolis(
    log_posterior: Callable[[np.ndarray], float],
    initial: np.ndarray,
    proposal_covariance: np.ndarray,
    seed: int,
    burn_in: int,
    draws: int,
    target_acceptance: float = 0.234,
) -> dict:
    """Sample with an adapt-during-burn-in Gaussian random-walk proposal."""
    if burn_in < 1 or draws < 1:
        raise ValueError("burn_in and draws must be positive")
    initial = np.asarray(initial, dtype=float)
    covariance = np.asarray(proposal_covariance, dtype=float)
    if covariance.shape != (len(initial), len(initial)):
        raise ValueError("Proposal covariance must match the initial vector")
    eigenvalues, eigenvectors = np.linalg.eigh((covariance + covariance.T) / 2)
    eigenvalues = np.maximum(eigenvalues, 1e-10)
    root = (eigenvectors * np.sqrt(eigenvalues)) @ eigenvectors.T
    rng = np.random.default_rng(seed)
    current = initial + 0.1 * root @ rng.normal(size=len(initial))
    current_log_posterior = float(log_posterior(current))
    if not np.isfinite(current_log_posterior):
        current = initial.copy()
        current_log_posterior = float(log_posterior(current))
    if not np.isfinite(current_log_posterior):
        raise ValueError("No finite posterior at the initial state")
    log_scale = float(np.log(2.38 / np.sqrt(len(initial))))
    samples = np.empty((draws, len(initial)))
    log_probabilities = np.empty(draws)
    accepted = np.zeros(burn_in + draws, dtype=bool)
    scales = np.empty(burn_in + draws)
    for index in range(burn_in + draws):
        proposal = current + np.exp(log_scale) * root @ rng.normal(size=len(initial))
        proposal_log_posterior = float(log_posterior(proposal))
        log_ratio = proposal_log_posterior - current_log_posterior
        if np.isfinite(proposal_log_posterior) and np.log(rng.random()) < log_ratio:
            current = proposal
            current_log_posterior = proposal_log_posterior
            accepted[index] = True
        if index < burn_in:
            learning_rate = min(0.05, 1.0 / np.sqrt(index + 10.0))
            log_scale += learning_rate * (float(accepted[index]) - target_acceptance)
        scales[index] = np.exp(log_scale)
        if index >= burn_in:
            retained = index - burn_in
            samples[retained] = current
            log_probabilities[retained] = current_log_posterior
    return {
        "draws": samples,
        "log_posterior": log_probabilities,
        "accepted": accepted,
        "proposal_scale": scales,
        "warmup_acceptance": float(np.mean(accepted[:burn_in])),
        "sampling_acceptance": float(np.mean(accepted[burn_in:])),
    }


def sample_independence_metropolis_t(
    log_posterior: Callable[[np.ndarray], float],
    location: np.ndarray,
    proposal_covariance: np.ndarray,
    seed: int,
    burn_in: int,
    draws: int,
    degrees_of_freedom: float = 5.0,
    scale: float = 1.0,
) -> dict:
    """Sample with a heavy-tailed independence proposal around a posterior mode."""
    if burn_in < 0 or draws < 1 or degrees_of_freedom <= 2 or scale <= 0:
        raise ValueError("Invalid independence-sampler settings")
    location = np.asarray(location, dtype=float)
    covariance = np.asarray(proposal_covariance, dtype=float)
    if covariance.shape != (len(location), len(location)):
        raise ValueError("Proposal covariance must match the location")
    eigenvalues, eigenvectors = np.linalg.eigh((covariance + covariance.T) / 2)
    eigenvalues = np.maximum(eigenvalues, 1e-10)
    root = scale * (eigenvectors * np.sqrt(eigenvalues)) @ eigenvectors.T
    inverse = (eigenvectors / (scale**2 * eigenvalues)) @ eigenvectors.T
    dimension = len(location)
    rng = np.random.default_rng(seed)

    def proposal_log_density(theta: np.ndarray) -> float:
        centered = theta - location
        squared_distance = float(centered @ inverse @ centered)
        return float(
            -0.5
            * (degrees_of_freedom + dimension)
            * np.log1p(squared_distance / degrees_of_freedom)
        )

    def propose() -> np.ndarray:
        gaussian = root @ rng.normal(size=dimension)
        radial = np.sqrt(rng.chisquare(degrees_of_freedom) / degrees_of_freedom)
        return location + gaussian / radial

    current = location.copy()
    current_log_posterior = float(log_posterior(current))
    if not np.isfinite(current_log_posterior):
        raise ValueError("No finite posterior at the proposal location")
    current_log_proposal = proposal_log_density(current)
    samples = np.empty((draws, dimension))
    log_probabilities = np.empty(draws)
    accepted = np.zeros(burn_in + draws, dtype=bool)
    for index in range(burn_in + draws):
        proposal = propose()
        proposal_log_posterior = float(log_posterior(proposal))
        proposal_log_proposal = proposal_log_density(proposal)
        log_ratio = (
            proposal_log_posterior
            - current_log_posterior
            + current_log_proposal
            - proposal_log_proposal
        )
        if np.isfinite(proposal_log_posterior) and np.log(rng.random()) < log_ratio:
            current = proposal
            current_log_posterior = proposal_log_posterior
            current_log_proposal = proposal_log_proposal
            accepted[index] = True
        if index >= burn_in:
            retained = index - burn_in
            samples[retained] = current
            log_probabilities[retained] = current_log_posterior
    return {
        "draws": samples,
        "log_posterior": log_probabilities,
        "accepted": accepted,
        "warmup_acceptance": float(np.mean(accepted[:burn_in])) if burn_in else None,
        "sampling_acceptance": float(np.mean(accepted[burn_in:])),
    }


def _split_chains(chains: np.ndarray) -> np.ndarray:
    chains = np.asarray(chains, dtype=float)
    if chains.ndim != 2 or chains.shape[0] < 2 or chains.shape[1] < 4:
        raise ValueError("Diagnostics require at least two chains and four draws")
    half = chains.shape[1] // 2
    return np.concatenate((chains[:, :half], chains[:, -half:]), axis=0)


def _rank_normalize(values: np.ndarray) -> np.ndarray:
    flattened = np.asarray(values, dtype=float).reshape(-1)
    ranks = rankdata(flattened, method="average")
    probabilities = (ranks - 3.0 / 8.0) / (len(ranks) + 1.0 / 4.0)
    return norm.ppf(probabilities).reshape(np.asarray(values).shape)


def _basic_rhat(chains: np.ndarray) -> float:
    chains = np.asarray(chains, dtype=float)
    draws = chains.shape[1]
    within = float(np.mean(np.var(chains, axis=1, ddof=1)))
    between = float(draws * np.var(np.mean(chains, axis=1), ddof=1))
    if within == 0:
        return 1.0 if between == 0 else np.inf
    variance = (draws - 1) / draws * within + between / draws
    return float(np.sqrt(variance / within))


def rank_normalized_rhat(chains: np.ndarray) -> float:
    """Return the maximum of rank-normalized and folded split R-hat."""
    split = _split_chains(chains)
    ranked = _rank_normalize(split)
    folded = _rank_normalize(np.abs(split - np.median(split)))
    return max(_basic_rhat(ranked), _basic_rhat(folded))


def _autocovariance(values: np.ndarray) -> np.ndarray:
    centered = np.asarray(values, dtype=float) - np.mean(values)
    size = len(centered)
    transformed = np.fft.rfft(centered, n=2 * size)
    covariance = np.fft.irfft(transformed * np.conjugate(transformed))[:size]
    return covariance / size


def bulk_effective_sample_size(chains: np.ndarray) -> float:
    """Estimate bulk ESS using rank normalization and Geyer's paired sequence."""
    split = _rank_normalize(_split_chains(chains))
    chain_count, draws = split.shape
    within = float(np.mean(np.var(split, axis=1, ddof=1)))
    between = float(draws * np.var(np.mean(split, axis=1), ddof=1))
    variance = (draws - 1) / draws * within + between / draws
    if variance <= 0:
        return float(chain_count * draws)
    autocovariances = np.asarray([_autocovariance(chain) for chain in split])
    correlations = np.ones(draws)
    for lag in range(1, draws):
        correlations[lag] = 1 - (within - float(np.mean(autocovariances[:, lag]))) / variance
    paired = []
    for index in range(0, draws - 1, 2):
        value = correlations[index] + correlations[index + 1]
        if value < 0:
            break
        if paired:
            value = min(value, paired[-1])
        paired.append(value)
    tau = max(-1 + 2 * sum(paired), 1.0)
    return float(min(chain_count * draws / tau, chain_count * draws))


def chain_diagnostics(chains: np.ndarray, names: tuple[str, ...]) -> dict[str, dict[str, float]]:
    """Calculate per-parameter rank R-hat and bulk ESS."""
    chains = np.asarray(chains, dtype=float)
    if chains.ndim != 3 or chains.shape[2] != len(names):
        raise ValueError("Chains must have chain x draw x parameter shape")
    return {
        name: {
            "rank_normalized_rhat": rank_normalized_rhat(chains[:, :, index]),
            "bulk_effective_sample_size": bulk_effective_sample_size(chains[:, :, index]),
        }
        for index, name in enumerate(names)
    }
