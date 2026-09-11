# Frozen core model v2 protocol

Status: **SPECIFIED BEFORE V2 IMPLEMENTATION OR RECOVERY**. The v1 recovery
failure and its paired ablations are known. No observational latent-state model
has been fitted, and no August 2025 holdout pixel array has been opened.

## Reason for a new version

Version 1 failed because 34.50% of prior-predictive values were outside the
preregistered trail-fraction range, latent-state RMSE exceeded half the simulated
observation noise, and annealing/process-scale SBC ranks were nonuniform. Both
pair offsets were free, leaving the latent origin weakly separated from a common
observation offset. Half-normal annealing also placed mass close to zero, where
long-baseline accumulation could become extreme.

The paired ablations support retaining event and background inputs. They do not
justify deleting annealing or process noise: removing process noise raised median
latent RMSE by 33.5%, and annealing removal usually lost BIC support despite an
unstable state-recovery effect.

## State and observation equations

The two-chip transition remains

\[
z_{k,i+1}=\exp(-\lambda\Delta t_i)z_{ki}
+\Delta t_i\left[b_0+s_k b_k+b_G G_i+b_E E_i\right]
+q\sqrt{\Delta t_i}\epsilon_{ki},
\]

with signs \(s_1=-1\) and \(s_2=+1\). The event and background covariates remain
standardized. The HST-like synthetic observation becomes

\[
y_{kpi}=z_{ki}+a\,\mathbf{1}(p=2)+r\eta_{kpi}.
\]

The first pair is therefore the exact zero reference and only the pair contrast
\(a\) is fitted. This defines the latent origin rather than estimating two
offsets against a weak initial-state anchor. The initial state mean remains zero
with fixed standard deviation 0.02, and the observation loading remains one.

## V2 priors and synthetic truth

Positive parameters are optimized in log coordinates with normal priors in that
coordinate, equivalent to the following log-normal physical priors. Values in
parentheses are log-scale standard deviations:

| Parameter | Prior median | Log SD | Synthetic truth |
|---|---:|---:|---:|
| Baseline drift \(b_0\) | 0.010 | 0.30 | 0.012 |
| Background response \(b_G\) | 0.008 | 0.40 | 0.008 |
| Event response \(b_E\) | 0.015 | 0.40 | 0.018 |
| Annealing \(\lambda\) | 0.080 | 0.30 | 0.060 |
| Process scale \(q\) | 0.006 | 0.35 | 0.008 |
| Observation scale \(r\) | 0.020 | 0.25 | 0.020 |

The signed chip deviation has prior N(0, 0.006^2) and truth 0.002. The pair
contrast has prior N(0, 0.015^2) and truth 0.010. These priors describe the
synthetic recovery regime; they are not observational detector calibrations.

## Disclosed prior-design exploration

Before freezing this protocol, three candidate scale sets were compared with
2,000 prior-predictive draws each using seed 20260911. The selected scales above
placed 0.0818% of values outside [-0.25, 0.75], compared with 1.473% for the
broad candidate and 0.437% for the intermediate candidate. This was prior design,
not a recovery run. V2 evaluation uses new fixed seeds: 831000–831099 for data,
1091000–1091099 for Laplace draws, and 541902 for the 1,000-draw prior gate.

## Unchanged recovery and failure gates

Run 100 independent 48-epoch recovery replicates. V2 passes only if all of the
following hold:

1. overall nominal 95% Laplace interval coverage is at least 0.90;
2. median absolute standardized ensemble bias for drift, event, background and
   annealing is below 0.35;
3. latent-state RMSE is below 0.0100, half the truth observation scale;
4. posterior-predictive 90% coverage is within [0.85, 0.95] and 95% coverage is
   within [0.90, 0.99];
5. at least 95 of 100 optimizations succeed;
6. at most 1% of prior-predictive values are outside [-0.25, 0.75]; and
7. every scalar SBC ten-bin chi-square p-value is at least 0.01 and every edge
   fraction is at most 0.20.

The finite-difference Laplace method, 512 draws per replicate, optimizer bounds
and covariate generator otherwise follow v1. Thresholds are unchanged after the
v1 result. A v2 failure will be retained and will continue to prohibit
observational interpretation.

## Downstream boundary

Even a v2 synthetic pass does not establish physical radiation inference. Before
observational interpretation, v2 must still undergo the exact-zero ablations,
lag/proxy sensitivity, whole-epoch forward validation and the frozen advanced
model thresholds. The temporal holdout remains sealed until those steps are
versioned and passed.
