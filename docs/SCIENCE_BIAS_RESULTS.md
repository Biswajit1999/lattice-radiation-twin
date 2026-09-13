# Conditional detector-to-science-bias result

The frozen Phase 10a Euclid image-domain experiment **fails its implementation
gate**. The conditional parallel-transfer calculation is numerically stable,
but the preregistered unweighted moment estimator does not retain enough valid
paired measurements in the low-signal cases. The failure is retained without
changing the estimator, sample, scenarios, or threshold after seeing the result.

## Gate result

Six of seven gates pass. Maximum relative charge-conservation error is
`4.55e-16`; zero-capture biases are exactly zero; the noiseless full-distance y
shift rises from `0.002405` to `0.024060` pixels as captured fraction rises; the
x control is exactly zero; all generated intervals are ordered; and forbidden
cross-mission amplitudes, dates, and posterior quantities are absent.

The measurement-validity gate requires at least 30 of 32 paired noise
realisations in every scenario. The minimum is 8 of 32, and 369 of 432 source
scenarios fall below the threshold. Background-subtracted unweighted moments can
have non-positive flux or trace at the frozen faint-source and high-background
settings. The broad ellipticity and size envelopes in the figure expose this
failure and are not validated uncertainty intervals.

## Bounded diagnostics

Across scenario medians, the conditional y-centroid shift spans approximately
`0.031` to `3.065` mas, with median `0.309` mas. The noiseless galaxy ring test
gives conditional multiplicative-response terms from about `-0.0252` to
`-0.00014`; its g1 additive terms span about `-0.0238` to `-0.00014`, while g2
additive terms remain numerically zero. These values diagnose the simulated
linear kernel and analytic Gaussian population only. Because the overall gate
fails, they are not Euclid performance requirements, cosmological shear
measurements, or observational predictions.

No posterior CTI uncertainty exists to propagate. HST science-bias propagation
remains blocked by the failed physical-inference gate, and Gaia propagation is
blocked by the unavailable public engineering CTI series. A follow-up estimator
must be specified as a new frozen experiment; it cannot replace or retroactively
repair this result.

Machine-readable output:
`results/science_bias/conditional_euclid_bias.json`.
