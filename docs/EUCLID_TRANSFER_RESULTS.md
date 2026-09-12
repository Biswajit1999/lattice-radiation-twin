# Euclid conditional-transfer result

Status: **NUMERICAL GATE PASS — CONDITIONAL SIMULATION ONLY**.

The frozen Phase 9 experiment evaluated 810 combinations of register, trap-
timescale sensitivity, species mixture, captured fraction, and transfer
distance. Every kernel was finite, non-negative, causal, and charge conserving.
The maximum kernel mass error was `3.33e-16`; the maximum relative propagated-
charge error was `7.28e-16`.

The mission inputs are specific to Euclid VIS: 153 K operation, 14.3 microsecond
serial transfers, 4.02 millisecond parallel transfers, 4096 x 4132 pixels per
CCD, a 6 x 6 focal plane, and published approximate emission-time features at
220 microseconds and 20 milliseconds. No HST or Gaia fitted parameter enters the
calculation.

For the nominal parallel timing, the represented conditional mean release lag
is approximately 1.000 pixels for the 220 microsecond feature and 5.492 pixels
for the 20 millisecond feature. The longest serial-timescale sensitivity leaves
up to 0.2312 of its release probability beyond the frozen 4096-pixel numerical
window; that probability is explicitly recorded and included in charge
conservation rather than discarded or renormalised.

## Interpretation

This result validates the implementation of a conditional release kernel. It
does not validate Euclid's trap density, capture probability, species mixture,
or radiation-damage trajectory. The fixed captured fractions of 0.1%, 0.3%, and
1% are diagnostic scenarios, not estimates or priors. The timescale factors of
0.5, 1, and 2 are sensitivity bounds around approximate published features, not
posterior intervals.

The simple kernel assumes capture at a transfer boundary and an exponential
release clock. It omits signal-dependent occupancy, recapture, four-phase and
tri-level sub-pixel clock dynamics, spatially varying shielding, and raw Euclid
trap-pumping reduction. These omissions prevent an observational amplitude or
calendar forecast. They also define the boundary for the next image-domain
science-bias experiment: report bias against explicit scenario amplitude,
mixture, and transfer position rather than mission date.

![Euclid conditional charge-release transfer](../paper/figures/euclid_conditional_transfer.png)
