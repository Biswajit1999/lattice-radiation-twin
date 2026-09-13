# Weighted detector-to-science-bias result

The frozen Phase 10b fixed Gaussian weighted-moment experiment **fails its
implementation gate**. Weighting improves the minimum valid-pair count from
8/32 in Phase 10a to 23/32, and reduces the number of scenarios below 30 valid
pairs from 369/432 to 42/432. It does not reach the preregistered 30/32 minimum.
The fixed 3-pixel weight, threshold and scenario population are retained.

All other gates pass. The run contains exactly 432 source and 54 ring scenarios;
all stored outputs are finite and intervals ordered; charge is conserved to
`4.55e-16`; zero-capture metrics and the x control are zero; the y shift is
positive and monotonic; claim boundaries are intact; and the Phase 10a result
and protocol hashes remain unchanged.

Across weighted scenario medians, y-centroid shift spans `0.016` to `1.136` mas
with median `0.140` mas. The noiseless weighted ring response gives
multiplicative terms from about `-0.00654` to `-0.000062`; g1 additive terms span
about `-0.00381` to `-0.000043`, and g2 additive terms remain numerically zero.
These are conditional diagnostics for the analytic image population. The failed
validity gate prevents promotion as validated uncertainty or mission performance.

Machine-readable output:
`results/science_bias/conditional_euclid_bias_weighted.json`.
