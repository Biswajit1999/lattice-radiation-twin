# Pinned ACSCCD calibration comparison

This is a new calibration experiment following the preserved RAW pilot, not a replacement tuned to improve its curve. Freeze configuration before evaluating calibrated measurements. The existing cohort is a development sample; independent epochs will be required for final validation.

Use the official `acsccd.e` stage from HSTCAL 3.2.0 under Linux, with CRDS context `hst_1356.pmap`. The HSTCAL conda package is available for Linux/macOS, not Windows; Ubuntu WSL is available on the build host. Preserve explicit package URLs and executable checksums. No hand-written electronics correction substitutes for ACSCCD.

Resolve CCDTAB, BIASFILE, OSCNTAB, BPIXTAB and SATUFILE against each RAW header. Pin downloaded reference bytes. Work on copies of RAW files. Enable DQICORR, BIASCORR and BLEVCORR; omit PCTECORR, DARKCORR and FLATCORR so that the damage-induced dark peaks and trails remain present. Sink correction remains omitted in the initial comparison and is a documented residual risk. ACSCCD supplies detector gain conversion, reference bias subtraction, prescan and supported post-servicing electronics corrections and DQ initialization. Require completed bias/overscan switches, positive populated gain values and ELECTRONS units in the outputs.

The resulting BLV intermediates are locally calibrated darks, not standard fully calibrated science FLTs. Keep original RAW bytes intact. Record source/reference/output hashes, calibration log and exact executable/version for each derived file. Retain commanded-gain, calibrated-gain and operational-state strata.

For extraction, retain hot/warm DQ bits 16/64 but reject all other nonzero DQ bits in peaks and trail/control samples. Freeze electron bins independently of the previous DN bins. Run the same direction, transfer-distance, signal, serial and blank controls, and report changed sample populations. Calibration is not proof that all control systematics are removed or trap parameters become identifiable.

Primary source: [ACS calibration processing steps](https://hst-docs.stsci.edu/acsdhb/chapter-3-acs-calibration-pipeline/3-4-calacs-processing-steps), [HSTCAL](https://github.com/spacetelescope/hstcal), [CRDS JSON services](https://hst-crds.stsci.edu/static/users_guide/web_services.html), accessed 2026-09-09.
