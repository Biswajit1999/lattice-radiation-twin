"""Create the frozen annual OMNI plan for the HST-through-holdout interval."""

from pathlib import Path

from lattice.provenance import write_json


def main():
    root = Path.cwd()
    plan = []
    for year in range(2003, 2026):
        plan.append(
            {
                "source_identifier": f"NASA-SPDF/OMNI2/hourly/{year}",
                "mission": "OMNI",
                "instrument": "multi-spacecraft compilation",
                "original_filename": f"omni2_{year}.dat",
                "tier": "A",
                "url": (f"https://spdf.gsfc.nasa.gov/pub/data/omni/low_res_omni/omni2_{year}.dat"),
                "processing_level": "hourly merged near-Earth environment",
                "pipeline_version": (
                    "OMNI2 annual ASCII; upstream revisable, retrieved bytes pinned by SHA-256"
                ),
                "usage_note": (
                    "NASA SPDF public scientific data; acknowledge OMNI and upstream PIs; "
                    "https://omniweb.gsfc.nasa.gov/html/ow_data.html"
                ),
                "selection_reason": (
                    "Complete calendar years from the first HST anchor through the 2025 holdout"
                ),
            }
        )
    write_json(root / "data/manifests/omni_continuous_plan.json", plan)
    print(f"Wrote frozen OMNI plan for {len(plan)} complete calendar years")


if __name__ == "__main__":
    main()
