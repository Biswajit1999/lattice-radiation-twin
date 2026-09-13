# Instrument geometry sources

The website focal-plane explorer is an explanatory rendering of published
hardware configuration. It does not replace engineering drawings and is not a
mechanical scale model. Device counts, active-pixel formats, pixel pitches,
readout segmentation and scan directions come from the primary sources below.

## HST ACS/WFC

- Source: [STScI ACS Instrument Handbook, detector design](https://hst-docs.stsci.edu/acsihb/chapter-3-acs-capabilities-design-and-operations/3-3-instrument-design)
- Readout source: [STScI ACS Instrument Handbook, CCD readout](https://hst-docs.stsci.edu/acsihb/chapter-4-detector-performance/4-2-the-ccds)
- Two SITe CCDs, each with a 4096 x 2048 active area.
- 15 x 15 micrometre pixels and approximately 0.05 arcsec sampling per pixel.
- Approximate 202 x 202 arcsec combined field of view.
- The two-chip gap is equivalent to approximately 50 pixels.
- Four amplifier quadrants (A/B on WFC1 and C/D on WFC2); parallel transfer
  feeds a serial register before horizontal transfer to an amplifier.

The website exaggerates the chip gap and register thickness so both remain
visible at mobile size.

## Gaia

- Source: [Gaia Collaboration, *The Gaia mission*, A&A 595 A1](https://doi.org/10.1051/0004-6361/201629272)
- Layout cross-check: [Rowell et al., Gaia EDR3 PSF/LSF calibration, A&A 649 A11](https://doi.org/10.1051/0004-6361/202039448)
- 106 CCDs and 938 million pixels in seven across-scan rows and 17 along-scan
  strips.
- Functional allocation: four metrology CCDs, 14 sky-mapper CCDs, 62
  astrometric-field CCDs, 14 BP/RP photometer CCDs and 12 RVS CCDs.
- Each CCD has 4500 TDI lines by 1966 across-scan columns, with 4494
  light-sensitive lines.
- Pixels are 10 x 30 micrometres along-scan by across-scan, corresponding to
  58.9 x 176.8 milliarcseconds.
- Fundamental TDI line period is 982.8 microseconds; integration per CCD is
  4.42 seconds. Source images and charge move along scan across the focal plane.

The website preserves the published functional occupancy and scan direction.
Package offsets and small mechanical separations are simplified.

## Euclid VIS

- Source: [Euclid Collaboration, *Euclid II. The VIS instrument*](https://doi.org/10.1051/0004-6361/202450996)
- Mission summary: [Euclid Consortium VIS instrument](https://www.euclid-ec.org/public/mission/vis/)
- 36 CCD273-84 devices in a 6 x 6 detector-plane array.
- Each device has 4096 x 4132 pixels at 12 x 12 micrometres.
- Each CCD has four quadrants with corner readout nodes: 144 channels in total.
- 609 million pixels cover approximately 0.57 square degrees at 0.1 arcsec
  sampling per pixel.

The website shows all 36 devices and four nodes per device. Device gaps and
node markers are enlarged for legibility.
