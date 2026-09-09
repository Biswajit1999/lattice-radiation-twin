# Data contract

Tier A: reproducible archival products. Tier B: genuinely public published calibration measurements. Tier C: explicitly synthetic truth. Digitised figures must be separately labelled with source and digitisation uncertainty; they are not raw mission data.

Every retrieved real-data file requires source identifier, mission, instrument, UTC retrieval timestamp, original filename, bytes, SHA-256, processing level, pipeline version (explicitly unknown if absent), licence/usage note, software commit and selection reason.

Raw caches are ignored. No invented mission measurements. Measured environment, exposure proxy, inferred state, simulation and forecast remain distinct.
