# Frozen Euclid conditional-transfer protocol

Protocol frozen: **2026-09-12**, before the production transfer run.

## Question and boundary

Can the public Euclid instrument configuration and explicitly published trap
timescales define a numerically valid, mission-specific forward charge-release
kernel? This experiment does not estimate Euclid's radiation damage amplitude
or forecast a calendar trajectory. Those quantities remain unidentified because
the processed Q1 trap and CTI time-series products are not distributed.

The experiment transfers model structure only. No fitted HST or Gaia amplitude,
trap density, shielding response, or detector parameter is an input. The HST
historical physical-inference gate remains closed.

## Frozen inputs

The committed `data/literature/euclid_constraints.json` provides:

- the 6 x 6 CCD273-84 focal plane and 4096 x 4132 active-pixel geometry;
- operating temperature of approximately 153 K;
- serial pixel-transfer duration of 14.3 microseconds;
- parallel row-transfer duration of 4.02 milliseconds;
- published emission-time features near 220 microseconds and 20 milliseconds.

No publication figure coordinates or Euclid image pixels are used. All input
files and the executing script must be SHA-256 recorded in the result.

## Forward model

For an electron captured by a trap with emission time constant `tau`, the
probability of release into downstream pixel lag `k >= 1` is

```text
K(k | tau, dt) = exp(-(k - 1) dt / tau) - exp(-k dt / tau).
```

The finite numerical kernel retains lags 1 through 4096 and records the omitted
tail probability rather than silently renormalising it. Serial and parallel
kernels use their own published transfer duration. Kernel mixtures use fixed
fast-species weights `{0, 0.25, 0.5, 0.75, 1}`. Emission-time sensitivities use
fixed multiplicative factors `{0.5, 1, 2}` around each approximate published
timescale. These are scenario bounds, not posterior uncertainty.

An impulse with input charge 100,000 electrons is propagated with full-array
captured fractions `{0.001, 0.003, 0.01}` and transfer-distance fractions
`{0.25, 0.5, 1}`. The effective captured fraction scales linearly with transfer
distance for this diagnostic only. The untrailed impulse plus all downstream
release pixels and the explicitly recorded beyond-window tail must conserve
charge.

## Frozen diagnostics and gates

The production result passes only if all of these hold over the entire grid:

1. all kernel entries and output charges are finite and non-negative;
2. release is causal, with no upstream charge;
3. kernel mass plus recorded tail differs from one by at most `1e-12`;
4. propagated charge plus recorded beyond-window charge differs from the input
   by at most `1e-9` relative;
5. the 20 ms parallel species has a larger conditional mean release lag than
   the 220 microsecond parallel species;
6. the published serial and parallel timing values are preserved exactly in the
   machine-readable output;
7. no observational Euclid amplitude, calendar forecast, or posterior interval
   is reported;
8. no HST or Gaia fitted parameter enters the computation.

The result is labelled **CONDITIONAL SIMULATION** even when every numerical gate
passes. A passing run opens later image-domain science-bias experiments at
explicit scenario amplitudes; it does not validate the amplitudes themselves.
