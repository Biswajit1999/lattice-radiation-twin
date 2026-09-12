from scripts.audit_gaia_availability import matching_tables, table_tokens


def test_table_tokens_do_not_confuse_galactic_with_cti():
    assert "cti" not in table_tokens("gaiadr3.total_galactic_extinction_map")


def test_matching_tables_requires_an_exact_schema_token():
    names = [
        "gaiadr3.total_galactic_extinction_map",
        "public.cti_calibration",
        "public.charge_injection",
    ]
    matches = matching_tables(names)
    assert matches["cti"] == ["public.cti_calibration"]
    assert matches["charge"] == ["public.charge_injection"]
    assert matches["calibration"] == ["public.cti_calibration"]
