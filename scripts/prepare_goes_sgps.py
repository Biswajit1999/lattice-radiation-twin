"""Archive NOAA daily-directory listings and freeze a GOES-R SGPS download plan."""

import calendar
import hashlib
import re
from datetime import UTC, date, datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from lattice.exposure import goes_version_key
from lattice.provenance import write_json

BASE = "https://data.ngdc.noaa.gov/platforms/solar-space-observing-satellites/goes"


def main():
    root = Path.cwd()
    metadata = root / "data/metadata/goes"
    metadata.mkdir(parents=True, exist_ok=True)
    plan, queries, exclusions = [], [], []
    satellite_years = {16: range(2020, 2025), 18: range(2025, 2026)}
    for satellite, years in satellite_years.items():
        for year in years:
            for month in range(1, 13):
                url = f"{BASE}/goes{satellite}/l2/data/sgps-l2-avg5m/{year}/{month:02d}/"
                request = Request(url, headers={"User-Agent": "LATTICE-research/0.1"})
                try:
                    with urlopen(request, timeout=60) as response:
                        content = response.read()
                except HTTPError as error:
                    if error.code != 404:
                        raise
                    queries.append(
                        {
                            "url": url,
                            "retrieved_at": datetime.now(UTC).isoformat(),
                            "status": "HTTP 404; monthly directory unavailable",
                        }
                    )
                    exclusions.append(
                        {
                            "month": f"{year}-{month:02d}",
                            "satellite": satellite,
                            "reason": "Monthly SGPS L2 directory unavailable",
                        }
                    )
                    continue
                snapshot = metadata / f"g{satellite}_{year}_{month:02d}.html"
                snapshot.write_bytes(content)
                digest = hashlib.sha256(content).hexdigest()
                queries.append(
                    {
                        "url": url,
                        "retrieved_at": datetime.now(UTC).isoformat(),
                        "snapshot_path": snapshot.relative_to(root).as_posix(),
                        "size_bytes": len(content),
                        "sha256": digest,
                        "status": "retrieved",
                    }
                )
                names = sorted(
                    set(
                        re.findall(
                            rf"sci_sgps-l2-avg5m_g{satellite}_d{year}{month:02d}\d{{2}}_v[\d-]+\.nc",
                            content.decode("utf-8"),
                        )
                    )
                )
                by_day = {}
                for name in names:
                    stamp = re.search(r"_d(\d{8})_", name)
                    if stamp is None:
                        raise ValueError(f"Cannot read date from {name}")
                    value = stamp.group(1)
                    day = date.fromisoformat(f"{value[:4]}-{value[4:6]}-{value[6:]}")
                    by_day.setdefault(day, []).append(name)
                expected_days = {
                    date(year, month, day)
                    for day in range(1, calendar.monthrange(year, month)[1] + 1)
                }
                exclusions.extend(
                    {
                        "date": day.isoformat(),
                        "satellite": satellite,
                        "reason": "No daily SGPS L2 science file in archived monthly listing",
                    }
                    for day in sorted(expected_days - by_day.keys())
                )
                for day, versions in sorted(by_day.items()):
                    versions.sort(key=goes_version_key)
                    selected = versions[-1]
                    if len(versions) > 1:
                        exclusions.extend(
                            {
                                "date": day.isoformat(),
                                "filename": name,
                                "reason": "Superseded by the highest numeric archived version",
                            }
                            for name in versions[:-1]
                        )
                    plan.append(
                        {
                            "source_identifier": f"NOAA-NCEI/GOES-{satellite}/SGPS/{day}",
                            "mission": f"GOES-{satellite}",
                            "instrument": "SEISS/SGPS",
                            "original_filename": selected,
                            "tier": "A",
                            "url": url + selected,
                            "processing_level": "Level 2 five-minute average",
                            "pipeline_version": selected.rsplit("_v", 1)[1].removesuffix(".nc"),
                            "usage_note": (
                                "NOAA NCEI public data; cite GOES-R SEISS L2 and retain NOAA "
                                "quality caveats"
                            ),
                            "selection_reason": (
                                "Every available daily science SGPS L2 average file in the "
                                "predeclared post-OMNI proton interval"
                            ),
                        }
                    )
    write_json(root / "data/manifests/goes_sgps_queries.json", queries)
    write_json(root / "data/manifests/goes_sgps_plan.json", plan)
    write_json(root / "data/manifests/goes_sgps_exclusions.json", exclusions)
    print(f"Frozen {len(plan)} daily SGPS files; recorded {len(exclusions)} exclusions")


if __name__ == "__main__":
    main()
