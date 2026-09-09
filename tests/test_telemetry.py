import pytest
from astropy.io import fits

from lattice.telemetry import read_support


def test_support_identity_and_uninterpreted_channels(tmp_path):
    primary = fits.PrimaryHDU()
    primary.header.update(ROOTNAME="example", INSTRUME="ACS")
    udl = fits.ImageHDU(name="UDL")
    udl.header["DETECTOR"] = "WFC"
    udl.header.update(JWDETMP1=-81.2, JWDETMP2=79.1, READPATT="--", JWROSPED=" ")
    path = tmp_path / "support.fits"
    fits.HDUList([primary, udl]).writeto(path)
    result = read_support(path, "example")
    assert result["channels"]["JWDETMP1"]["value"] == -81.2
    assert result["channels"]["JWDETMP2"]["value"] == 79.1
    assert result["channels"]["READPATT"]["value"] is None
    assert result["operating_temperature_K"] is None
    with pytest.raises(ValueError, match="match exposure"):
        read_support(path, "another")
