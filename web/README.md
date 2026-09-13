# LATTICE research interface

The static React/TypeScript site reads `public/data/evidence.json`, generated
from repository results by `python scripts/export_web_data.py`. It does not
contain hard-coded scientific measurements.

```sh
python scripts/export_web_data.py
cd web
npm ci
npm run lint
npm run build
npm run dev
```

The Three.js environment scene is lazy loaded and explicitly schematic. A text
mission inventory remains available without WebGL. Motion respects the live
reduced-motion preference, and the rotating scene has a pause control plus
keyboard camera controls. The evidence chart has a text summary and table.

GitHub Pages uses the `/lattice-radiation-twin/` base path. The deployment
workflow regenerates evidence from the exact deployed commit before building.
