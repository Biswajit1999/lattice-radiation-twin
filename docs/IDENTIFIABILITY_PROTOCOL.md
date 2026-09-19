# Historical component-identifiability audit

## Question

Can the eight-epoch HST historical summary design distinguish four cumulative
radiation proxy components from calendar time well enough to interpret their
individual regression coefficients?

## Design

The audit uses only the already-open 2003--2024 replication summaries committed
in `results/baselines/historical_forward_chaining.json`. Predictor values are
identical across the four detector strata within an epoch, so they are collapsed
to one independent predictor row per epoch. Outcomes are combined only for the
leave-one-epoch coefficient diagnostic using inverse-variance weights. The six
August 2025 temporal-holdout FITS arrays remain sealed.

The design matrix contains an intercept, standardized calendar time, and four
standardized cumulative proxies: OMNI event, OMNI background, SGPS event, and
SGPS background. The audit reports rank, residual degrees of freedom, condition
number, correlations, variance-inflation factors (VIFs), exposure singular
values, and standardized coefficients from eight leave-one-epoch-out fits.

## Diagnostic gates

This is a post hoc design audit, not a preregistered hypothesis test. Its
versioned component-attribution gate requires all of the following:

1. absolute pairwise correlation among exposure components below 0.95;
2. every predictor VIF below 10;
3. at least four residual degrees of freedom, one per exposure component; and
4. the sign of every exposure coefficient to remain stable across all eight
   leave-one-epoch-out fits.

The thresholds are screening rules for this repository, not universal laws.
Failing the gate means component coefficients are not interpretable from this
design; it does not imply that the measured longitudinal detector trend is
spurious. Passing would not establish causality.

## Reproduction

```sh
python scripts/run_identifiability_audit.py
```
