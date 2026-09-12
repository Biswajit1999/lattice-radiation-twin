# Data contract

Tier A: reproducible archival products. Tier B: genuinely public published calibration measurements. Tier C: explicitly synthetic truth. Digitised figures must be separately labelled with source and digitisation uncertainty; they are not raw mission data.

Every retrieved real-data file requires source identifier, mission, instrument, UTC retrieval timestamp, original filename, bytes, SHA-256, processing level, pipeline version (explicitly unknown if absent), licence/usage note, software commit and selection reason.

Raw caches are ignored. No invented mission measurements. Measured environment, exposure proxy, inferred state, simulation and forecast remain distinct.

## Acquisition and replay

`lattice fetch-omni --years 2003 2014 2023` downloads bounded annual ASCII objects. These calendar years were selected before examining their values: early ACS, Gaia launch era and Euclid launch era. This is an ingestion pilot, not a continuous exposure series. `lattice verify data/manifests/omni.json` checks bytes against the manifest. A frozen JSON plan can be retrieved with `lattice fetch-plan PLAN.json`; existing records pin SHA-256 for re-download. A changed upstream object raises an error rather than replacing the recorded version silently. New retrieval timestamps may differ; scientific bytes must match. Interrupted or oversized downloads are discarded. The cache is content-addressed.

Unknown pipeline versions must say why they are unknown. The upstream URL, identifier, selection and usage note are mandatory. The acquisition software commit identifies source code used at retrieval; production data acquisition occurs after the corresponding implementation checkpoint. Source changes since HEAD must be disclosed before interpreting a retrieval.

## Measurement schema to be frozen for HST

Each measurement must carry observation ID, source SHA-256, UTC MJD, exposure time, chip/amplifier, image orientation and transfer distance, signal/background bins, DQ selection, sample population, estimator, uncertainty method, temperature and calibration/reference headers. Missing operational values remain null with a reason. An FLT/FLC difference is a pipeline transformation, not an independent ground-truth CTI measurement. Cosmic rays and hot pixels must not be conflated.

## Current availability gates

- HST MAST: public dark/FLT/FLC archive targeted; live query is being tested. CRDS dark products are a possible reference-data route, but corrected references cannot be assumed to preserve uncorrected CTI trails.
- OMNI: hourly products reachable. The official documentation limits energetic proton flux coverage to 2020-03-04; later years still include solar/geomagnetic indices. Fill values are missing, never zero flux.
- NOAA: legacy GOES and GOES-R SEISS archive locations verified in the literature audit; calibrated cross-satellite joins, X-rays and event lists are not yet ingested.
- Euclid Q1: ESA lists public calibrated multi-extension VIS frames; actual frame retrieval and metadata verification remain pending.
- Gaia Tier B: a 2026-09-12 live audit of 248 official Gaia TAP tables found no exact CTI, charge-injection, calibration or engineering table. Explicit prose/table constraints from Pagani et al. are stored separately from mission data; no figure was digitised.
- Euclid Tier B: no granular machine-readable trap-pumping series located in the targeted search. Literature constraints may be used with exact citations, never invented observations.

Usage is source-specific. The repository's software licence does not relicense mission data. A future derived product must retain the original acknowledgement and redistribution conditions.
