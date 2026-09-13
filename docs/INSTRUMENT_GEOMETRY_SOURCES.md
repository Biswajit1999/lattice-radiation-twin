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

## Field plate spacecraft and distance geometry

- Hubble dimensions and orbit: [NASA, Hubble by the Numbers](https://science.nasa.gov/mission/hubble/overview/hubble-by-the-numbers/)
  gives a 13 m length, 4.3 m width and an approximate 483 km altitude.
- Hubble rendering: [NASA 3D Resources, Hubble Space Telescope (A)](https://science.nasa.gov/3d-resources/hubble-space-telescope-a/).
  The checked-in GLB is the 1.62 MB original published by NASA, rather than a
  locally reconstructed spacecraft silhouette. SHA-256:
  `e5ba4de15c7d359ac8fa1ab7e286aff42dec09c0fadae3db99252587f39fa384`.
- Earth surface: [NASA Scientific Visualization Studio, Blue Marble 2015](https://svs.gsfc.nasa.gov/30763).
  The checked-in 1024 x 512 texture is the published VIIRS flat-map image.
  SHA-256: `05d3279dec9fc8204a0eaf0433344c5052a58e794d040337cc5050fc356486f0`.
- Sun-Earth baseline: [NASA Basics of Space Flight](https://science.nasa.gov/learn/basics-of-space-flight/chapter1-1/)
  reports 149,600,000 km and 8.3 light-minutes for the Sun-to-Earth distance.
- Sun-Earth L2: [NASA Universe glossary](https://science.nasa.gov/universe/glossary/)
  places L2 about 1.5 million km from Earth on the anti-Sun side.
- Gaia: [ESA Gaia factsheet](https://www.esa.int/Science_Exploration/Space_Science/Gaia/Gaia_factsheet)
  gives a 10 m deployed span and Lissajous-type L2 orbit; [ESA sunshield
  deployment](https://www.esa.int/ESA_Multimedia/Videos/2013/06/Gaia_sunshade_deployment)
  describes its 12 rectangular panels and 12 triangular infill sections.
- Euclid: [ESA Euclid overview](https://www.esa.int/Science_Exploration/Space_Science/Euclid_overview)
  gives a 4.7 m height, 3.7 m diameter and 1.2 m telescope.

The plate preserves the physical order Sun -> Earth -> Sun-Earth L2 and shows
the measured distances numerically. It deliberately uses separate display
scales for distance, celestial bodies and spacecraft. At one linear scale,
Hubble and the L2 observatories would be sub-pixel at the displayed width.
