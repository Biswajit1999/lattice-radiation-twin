from scripts.audit_euclid_availability import (
    matching_tables,
    parse_tables,
    summarize_raw_inventory,
)


def test_parse_tables_retains_hierarchy_and_sorted_names():
    xml = b"""<tableset xmlns='urn:test' xmlns:e='urn:esa'>
      <schema><table e:hierarchy='Q1/Level 2'><name>q1.vis_frame</name></table>
      <table e:hierarchy='Q1/Level 1'><name>q1.raw_trap</name></table></schema>
    </tableset>"""
    assert parse_tables(xml) == [
        {"name": "q1.raw_trap", "hierarchy": "Q1/Level 1"},
        {"name": "q1.vis_frame", "hierarchy": "Q1/Level 2"},
    ]


def test_matching_tables_requires_exact_tokens():
    tables = [
        {"name": "q1.attribution", "hierarchy": "Q1"},
        {"name": "q1.cti_model", "hierarchy": "Q1/Calibration"},
        {"name": "q1.trap_pumping", "hierarchy": "Q1/Calibration"},
    ]
    matches = matching_tables(tables)
    assert matches["cti"] == ["q1.cti_model"]
    assert matches["trap"] == ["q1.trap_pumping"]
    assert matches["pumping"] == ["q1.trap_pumping"]


def test_summarize_raw_inventory_separates_product_kinds():
    rows = [
        {"category": "SCIENCE", "first_type": "SURVEY", "second_type": "OTHER"},
        {"category": "CALIB", "first_type": "TRAP_PUMPING", "second_type": "PARALLEL"},
        {"category": "CALIB", "first_type": "TRAP_PUMPING", "second_type": "PARALLEL"},
    ]
    summary = summarize_raw_inventory(rows)
    assert summary["vis_raw_frame_count"] == 3
    assert summary["counts_by_kind"][0]["count"] == 2
    assert summary["counts_by_kind"][1]["count"] == 1
