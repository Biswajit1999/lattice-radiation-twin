# Euclid public-data availability result

Status: **PIXEL-DOMAIN TRANSFER OPEN — processed damage amplitude unavailable**.

The Phase 9 availability audit queried the public ESA Euclid Science Archive Q1
TAP service on 2026-09-12. The live schema contained 103 tables. Direct archive
queries found 836 calibrated VIS quad-frame records and 1,112 raw VIS records.
The raw inventory includes 36 parallel trap-pumping frames acquired from
2024-07-17 through 2024-09-08. Each frame maps to 36 detector records, for 1,296
detector records in total. An 80-byte range probe of the first public product
returned a valid FITS signature. No full image product was downloaded during
this checkpoint.

The [official Q1 VIS product release
matrix](https://euclid.esac.esa.int/dr/q1/dpdd/visdpd/visintro.html) separately
lists `DpdVisCTICalibrationResults`, `DpdVisCTITimeEvolutionModel`,
`DpdVisTrapPumpingModel`, and `DpdVisTrapPumpingResults` as not distributed in
Q1. The archive therefore exposes raw trap-pumping inputs but not the processed
per-trap catalogue or longitudinal CTI model required to identify an
observational Euclid damage amplitude.

## What the public frames support

The calibrated VIS frames can establish the focal-plane geometry, signal and
background distributions, source morphology, detector-position dependence,
noise regime, and calibration metadata. The raw trap-pumping frames can support
a later Euclid-specific reduction after the multi-frame clock sequence and
quality-control procedure are independently reproduced and tested. A raw FITS
file is not itself a machine-readable trap time series.

Published constraints are stored in
`data/literature/euclid_constraints.json`. They include the 6 x 6 CCD layout,
the approximately 153 K focal-plane temperature, reported emission-time
features near 220 microseconds and 20 milliseconds, early performance-
verification epochs, and the qualitative first-year damage evolution. No value
was inferred from a publication figure.

Q2 was released on 2026-06-24 under DOI
[10.57780/esa-ab289b7](https://doi.org/10.57780/esa-ab289b7). Its advertised
scope is Galactic-bulge VIS images, astrometry, and photometry; it does not add
a public trap-pumping result product.

## Transfer boundary

A forward pixel simulation may now use the public Euclid geometry and noise
domain plus explicitly published trap timescales. Any damage level must remain
labelled simulated or inferred. The repository will not copy the failed HST
historical amplitude or the unavailable Gaia amplitude into Euclid. A full raw
trap-pumping download and reduction is deferred until its size and validation
plan are bounded.

![Euclid Q1 public-product availability audit](../paper/figures/euclid_availability_audit.png)
