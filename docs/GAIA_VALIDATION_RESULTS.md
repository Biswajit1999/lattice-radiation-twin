# Gaia external-validation availability result

Status: **DIRECT QUANTITATIVE VALIDATION BLOCKED — literature constraints
retained**.

The Phase 8 audit queried the official ESA Gaia Archive TAP schema through
`astroquery.gaia` on 2026-09-12. It returned 248 public tables. Exact schema-token
searches found no `cti`, `charge`, `injection`, `calibration` or `engineering`
table. The archived table names, query time and checks are stored in
`results/gaia/availability_audit.json`.

This is a bounded negative search result rather than proof that no suitable data
exist anywhere. The [Gaia archive](https://gea.esac.esa.int/archive/) publishes
science-release tables, while the [Gaia DR2 spacecraft-status
documentation](https://gea.esac.esa.int/archive/documentation/GDR2/Introduction/chap_cu0int/cu0int_sec_release_framework/cu0int_sssec_spacecraft_status.html)
describes first-pixel-response and serial-CTI engineering diagnostics. The audit
did not locate those engineering measurements as public archive tables.

## Published constraints

The machine-readable literature table
`data/literature/gaia_constraints.json` transcribes only values explicitly stated
in [Pagani et al. (2026)](https://arxiv.org/abs/2601.19353), DOI
10.1051/0004-6361/202557540. It records:

- 26 serial-CTI engineering activities at a cadence of roughly 3–4 months;
- a final activity on 2025-01-14 at OBMT 16381;
- gradual damage accumulation reported as steeper near solar minimum;
- an approximately 20% trail-level step after the 2017-09-10 solar event at
  OBMT 5651;
- in-flight parallel CTI around one eighth of the pre-launch prediction; and
- the 2025-03-06 end-of-life annealing intervention and its reported serial-CTI
  step.

No value was inferred from figure coordinates. Device-level trails and fitted
CtiPixel parameters remain unavailable to this repository.

## L2 proxy comparison

LATTICE's shared L2 basis contains a positive SEP-event term and an inverse-F10.7
background term. Those structures are qualitatively consistent with the
published event-plus-gradual description. The local environment layer marks
September 2017 as a threshold-event month; its shared SEP proxy is 4.1045 and
ranks seventh among 200 OMNI months. This verifies timing consistency with the
reported Gaia event, not radiation transport or detector amplitude. OMNI is a
near-Earth measurement rather than Gaia dose at L2.

The required quantitative question—whether the L2 model predicts Gaia damage
better than the HST functional form—cannot be scored without a public calibration
series and uncertainties. Direct Gaia validation is therefore blocked, and no
HST parameter amplitude is transferred to Gaia. Figure digitisation remains
prohibited for the main validation set.

![Gaia public-data and literature-constraint audit](../paper/figures/gaia_literature_validation.png)
