# Forced-response detector-to-science-bias result

The frozen Phase 10c fixed-template linearized response experiment **passes all
implementation gates**. All 432 source scenarios retain 32/32 finite paired
responses, all 54 noiseless ring scenarios are finite, intervals are ordered,
and maximum relative charge-conservation error is `4.55e-16`. Zero-capture
responses and the x control are zero, the y response is positive and monotonic,
and all four predecessor result/protocol hashes remain unchanged.

Across scenario medians, the forced y-centroid response spans `0.0164` to
`1.1345` mas with median `0.1391` mas. Weighted-flux response spans `-0.00560`
to `-0.0000273`, linearized e1 response spans `-0.02884` to `-0.0000570`, and
linearized trace-size response spans `-0.00218` to `0.02620`. The fixed weighted
ring test gives multiplicative terms from about `-0.00654` to `-0.000062`; g1
additive terms span about `-0.00381` to `-0.000043`, while g2 additive terms are
numerically zero.

This pass establishes stable computation for a controlled fixed-template
injection response. It does not validate a blind survey measurement pipeline,
the conditional captured fractions, the linear CTI approximation, or Euclid
performance. No observed damage amplitude or posterior CTI state is available,
so the ranges are sensitivity envelopes rather than posterior uncertainty.
HST and Gaia propagation remain blocked at their documented gates.

Machine-readable output:
`results/science_bias/conditional_euclid_bias_forced.json`.
