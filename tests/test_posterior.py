import numpy as np

from lattice.posterior import (
    bulk_effective_sample_size,
    chain_diagnostics,
    rank_normalized_rhat,
    sample_elliptical_slice,
    sample_independence_metropolis_t,
    sample_random_walk_metropolis,
)


def gaussian_chain(seed):
    observation = 1.0
    observation_sd = 0.5

    def log_likelihood(theta):
        return -0.5 * ((observation - theta[0]) / observation_sd) ** 2

    return sample_elliptical_slice(
        log_likelihood,
        prior_mean=np.asarray([0.0]),
        prior_sd=np.asarray([1.0]),
        seed=seed,
        burn_in=300,
        draws=1200,
    )["draws"][:, 0]


def test_elliptical_slice_recovers_conjugate_gaussian_posterior():
    draws = np.concatenate((gaussian_chain(810), gaussian_chain(811)))
    np.testing.assert_allclose(np.mean(draws), 0.8, atol=0.04)
    np.testing.assert_allclose(np.var(draws), 0.2, atol=0.04)


def test_elliptical_slice_is_deterministic_for_fixed_seed():
    first = gaussian_chain(915)
    second = gaussian_chain(915)
    np.testing.assert_array_equal(first, second)


def test_rank_diagnostics_accept_independent_chains():
    rng = np.random.default_rng(72)
    chains = rng.normal(size=(4, 1000))
    assert rank_normalized_rhat(chains) < 1.05
    assert bulk_effective_sample_size(chains) > 500


def test_rank_rhat_rejects_separated_chains():
    rng = np.random.default_rng(91)
    chains = np.vstack((rng.normal(-2, 1, 1000), rng.normal(2, 1, 1000)))
    assert rank_normalized_rhat(chains) > 1.1


def test_chain_diagnostic_shape_contract():
    rng = np.random.default_rng(118)
    chains = rng.normal(size=(2, 500, 2))
    result = chain_diagnostics(chains, ("a", "b"))
    assert set(result) == {"a", "b"}


def test_preconditioned_metropolis_recovers_correlated_gaussian():
    covariance = np.asarray([[1.0, 0.8], [0.8, 1.5]])
    precision = np.linalg.inv(covariance)

    def log_posterior(theta):
        return -0.5 * theta @ precision @ theta

    chains = np.asarray(
        [
            sample_random_walk_metropolis(
                log_posterior,
                initial=np.zeros(2),
                proposal_covariance=covariance,
                seed=1200 + chain,
                burn_in=500,
                draws=2500,
            )["draws"]
            for chain in range(2)
        ]
    )
    np.testing.assert_allclose(np.mean(chains, axis=(0, 1)), np.zeros(2), atol=0.12)
    np.testing.assert_allclose(np.cov(chains.reshape(-1, 2), rowvar=False), covariance, atol=0.12)
    diagnostics = chain_diagnostics(chains, ("a", "b"))
    assert max(value["rank_normalized_rhat"] for value in diagnostics.values()) < 1.05


def test_independence_metropolis_recovers_correlated_gaussian():
    covariance = np.asarray([[1.0, 0.8], [0.8, 1.5]])
    precision = np.linalg.inv(covariance)

    def log_posterior(theta):
        return -0.5 * theta @ precision @ theta

    results = [
        sample_independence_metropolis_t(
            log_posterior,
            location=np.zeros(2),
            proposal_covariance=covariance,
            seed=2200 + chain,
            burn_in=100,
            draws=2500,
        )
        for chain in range(2)
    ]
    chains = np.asarray([row["draws"] for row in results])
    np.testing.assert_allclose(np.mean(chains, axis=(0, 1)), np.zeros(2), atol=0.08)
    np.testing.assert_allclose(np.cov(chains.reshape(-1, 2), rowvar=False), covariance, atol=0.12)
    assert min(row["sampling_acceptance"] for row in results) > 0.5
