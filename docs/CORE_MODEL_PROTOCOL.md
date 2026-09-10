# Frozen core LATTICE model protocol

Status: **SPECIFIED BEFORE IMPLEMENTATION OR OBSERVATIONAL FITTING**. The historical B0–B5 result is known. No August 2025 holdout pixel array has been opened.

## Computational choice

The first core implementation will use an exact linear-Gaussian state-space likelihood and smoother written against pinned NumPy/SciPy. PyMC, JAX and NumPyro are not present in the tested environment. Adding one would introduce a large untested runtime without improving this model’s exact Gaussian calculations. The custom implementation must expose every matrix, prior and transform and will be replaced or cross-checked if later observation models require non-Gaussian sampling.

## State and transition

For mission (m), detector group (k), and interval (i), latent damage (z_{mki}) evolves as

\[
z_{mk,i+1}=\exp(-\lambda_m\Delta t_i)z_{mki}
+\Delta t_i\left[b_{0m}+b_{km}+b_{Gm}G_i+b_{Em}E_i\right]
+q_m\sqrt{\Delta t_i}\epsilon_{mki}.
\]

(G_i) is the continuous-background basis and (E_i) is the event basis. Their coefficients are mission-specific. The non-negative (lambda_m) is optional annealing; (lambda_m=0) is an explicit ablation. Process innovations are standard normal. No term is called physical dose.

The initial HST observation model is

\[
y_{kpi}=a_p+z_{HST,ki}+r_{HST}\eta_{kpi},
\]

where (p) is replication pair index and the observation loading is fixed to one. Gaia and Euclid will receive separate observation amplitudes, offsets and noise after their evidence is acquired; they will not inherit the HST observation equation.

## Identifiability constraints and priors

The initial state mean is fixed at zero and its standard deviation is fixed at 0.02. Fixing the HST observation loading to one removes the state/amplitude scaling symmetry. Detector-group deviations sum to zero. Exposure columns are centered and scaled inside each training fold. Pair offsets use (N(0,0.1^2)); drift and standardized exposure coefficients use (N(0,0.05^2)); the chip deviation uses (N(0,0.025^2)). Process and observation scales use half-normal priors with scales 0.03 and 0.05. Annealing uses half-normal scale 0.2 yr(^{-1}). Optimization occurs in unconstrained log-scale coordinates for positive parameters.

## Synthetic-truth gate

Before fitting observational outcomes, generate at least 48 epochs with known parameters under fixed seeds. Run 100 independent recovery replicates. The gate passes only if:

1. at least 90% of true scalar parameters fall inside nominal 95% Laplace intervals;
2. median absolute standardized bias is below 0.35 for drift, event, background and annealing terms;
3. latent-state RMSE is below 0.5 times the simulated observation-noise scale;
4. 90% and 95% posterior-predictive coverage fall within [0.85, 0.95] and [0.90, 0.99], respectively; and
5. the optimizer succeeds in at least 95 of 100 replicates.

Failure closes observational interpretation. Thresholds will not be weakened after seeing recovery results.

## Required checks

Prior-predictive simulation must reject a specification if more than 1% of trail fractions lie outside [-0.25, 0.75]. Simulation-based calibration will rank recovered scalar parameters over the 100 replicates; obvious edge pile-up or a chi-square uniformity p-value below 0.01 is a failure flag. Required ablations remove annealing, event input, continuous background and process noise one at a time. Lag sensitivity is fixed at 0, 1, 3, 6 and 12 completed months, chosen inside each training fold only. Proxy sensitivity compares total-particle B3 and event/background B4 bases.

Any observational model must use the same whole-epoch forward folds as B0–B5. It justifies complexity only at RMSE ≤ 0.0382313, mean NLPD < -1.78239 and 95% interval coverage ≥ 0.75. It cannot open the physical-inference gate unless it also passes synthetic recovery, predictive checks, identifiability diagnostics and the exposure ablations.

No neural ODE, Gaussian-process residual or neural state-space residual is permitted until the interpretable state model passes these gates. The August 2025 holdout remains sealed until implementation, optimization bounds and failure behaviour are verified and checkpointed.
