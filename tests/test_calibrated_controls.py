import numpy as np

from lattice.hst import dq_sample_mask


def test_hot_pixels_retained_but_saturated_trails_rejected():
    a = np.zeros((64, 64), dtype=np.uint16)
    b = np.zeros_like(a)
    a[32, 32] = 16
    b[32, 32] = 64
    assert dq_sample_mask(a, b)[32, 32]
    b[35, 32] = 256
    assert not dq_sample_mask(a, b)[32, 32]


def test_bad_blank_background_sample_rejected():
    a = np.zeros((64, 64), dtype=np.uint16)
    b = np.zeros_like(a)
    b[32, 44] = 128
    assert not dq_sample_mask(a, b)[32, 32]
    assert not dq_sample_mask(a, b)[1, 1]
