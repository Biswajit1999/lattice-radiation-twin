# Pinned ACSCCD calibration comparison

This is a new calibration experiment following the preserved RAW pilot, not a replacement tuned to improve its curve. Freeze configuration before evaluating calibrated measurements. The existing cohort is a development sample; independent epochs will be required for final validation.

Use the official `acsccd.e` stage from HSTCAL 3.2.0 under Linux, with CRDS context `hst_1356.pmap`. The HSTCAL conda package is available for Linux/macOS, not Windows; Ubuntu WSL is available on the build host. Preserve explicit package URLs and executable checksums. No hand-written electronics correction substitutes for ACSCCD.

Resolve CCDTAB, BIASFILE, OSCNTAB, BPIXTAB and SATUFILE against each RAW header. Pin downloaded reference bytes. Work on copies of RAW files. Enable DQICORR, BIASCORR and BLEVCORR; omit PCTECORR, DARKCORR and FLATCORR so that the damage-induced dark peaks and trails remain present. Sink correction remains omitted in the initial comparison and is a documented residual risk. ACSCCD supplies detector gain conversion, reference bias subtraction, prescan and supported post-servicing electronics corrections and DQ initialization. Require completed bias/overscan switches, positive populated gain values and ELECTRONS units in the outputs.

The resulting BLV intermediates are locally calibrated darks, not standard fully calibrated science FLTs. Keep original RAW bytes intact. Record source/reference/output hashes, calibration log and exact executable/version for each derived file. Retain commanded-gain, calibrated-gain and operational-state strata.

For extraction, retain hot/warm DQ bits 16/64 but reject all other nonzero DQ bits in peaks and trail/control samples. Freeze electron bins independently of the previous DN bins. Run the same direction, transfer-distance, signal, serial and blank controls, and report changed sample populations. Calibration is not proof that all control systematics are removed or trap parameters become identifiable.

Primary source: [ACS calibration processing steps](https://hst-docs.stsci.edu/acsdhb/chapter-3-acs-calibration-pipeline/3-4-calacs-processing-steps), [HSTCAL](https://github.com/spacetelescope/hstcal), [CRDS JSON services](https://hst-crds.stsci.edu/static/users_guide/web_services.html), accessed 2026-09-09.

Before calibrated extraction, freeze signal bins at 100-300, 300-1000 and 1000-3000 electrons; primary selection 300-1000 electrons, 1024-2032 parallel transfers. This changes populations relative to native DN and will be reported. The installed HSTCAL 3.2.0 contains ACSCCD 10.4.1 (08-Aug-2025). Explicit Linux package URLs are in hstcal-linux-explicit.txt.

## Development result

All 16 frozen RAW exposures were processed successfully and all 17 referenced CRDS objects, RAW inputs, logs and output hashes verify. The primary calibrated selection contains 55,031 peaks. Both chips are consistent with zero in 2003; by 2024 the mean observable is 0.2311 for WFC1 (95% column-bootstrap interval 0.1864–0.2714) and 0.2203 for WFC2 (0.1804–0.2605). Signal/transfer panels show the expected general increase with transfer distance most clearly in the 300–1000 and 1000–3000 electron strata.

The calibrated gate remains closed. The 2012 WFC2 offset-column blank control excludes zero at the unadjusted nominal 95% level (mean 0.0736, interval 0.0072–0.1748). Calibrated background medians range from about 3 electrons in 2003 to about 73 electrons in the flashed 2024 pair; the 2015, 2018 and 2024 samples are post-flashed while the selected 2021 pair is not. The comparison has only one pair per epoch, temperature-sensor interpretation and pixel dwell times remain unresolved, and sink/calibration uncertainty is not propagated. The result demonstrates a reproducible longitudinal trailing observable, not radiation causation, a dose response, or identifiable trap populations. Exact values and limitations are in `results/hst_calibrated/validation_gate.json`.
