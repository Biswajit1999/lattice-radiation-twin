# Conditional-kernel numerical validation

Status: synthetic numerical validation only. These tests do not estimate HST
or Euclid trap populations and do not reopen the failed historical attribution
gate.

## Tail truncation

For exponential release with time constant `tau`, step `dt`, and `N` output
lags, the omitted probability is exactly

`P_tail = exp(-N dt / tau)`.

The sweep calculates the minimum integer `N` for omitted-mass budgets from
`1e-3` to `1e-12`, verifies mass closure, and records the physical window in
seconds. This makes the numerical truncation choice auditable for every
sensitivity timescale.

## Synthetic mixture recovery

Two ordered exponential components are injected into a multinomial release
histogram. A bounded nonlinear least-squares fit recovers fast/slow timescales
and mixture weight while retaining the beyond-window tail as an explicit bin.
Count levels from `1e5` to `1e7` electrons quantify bias and information-matrix
conditioning. The selected synthetic timescales are an identifiability test,
not physical detector calibration.

## Finite image-window convergence

A noiseless Gaussian source is trailed with the existing conditional kernel on
images from 24 to 128 pixels high. The experiment records charge closure,
overflow, centroid shift, and relative change against the largest window. This
separates finite-array numerical error from detector-physics uncertainty.

## Reproduce

```bash
python scripts/run_kernel_validation.py
pytest -q tests/test_kernel_validation.py
```

Machine-readable results are under `results/numerical_validation/`; the figure
is `paper/figures/kernel_numerical_validation.png`.
