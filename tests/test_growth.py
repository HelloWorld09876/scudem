import numpy as np
import pytest

from pedsocket.growth import centile_curve, lms_table, preece_baines


@pytest.mark.parametrize("sex", ["boy", "girl"])
def test_preece_baines_fits_cdc_median_within_one_cm(sex, boy, girl):
    child = boy if sex == "boy" else girl
    assert child.pb_rmse_cm < 1.0


def test_ode_solution_matches_closed_form(boy):
    ages = np.linspace(4.0, 20.0, 50)
    closed = preece_baines(ages, *boy.pb) / 100.0
    assert np.max(np.abs(boy.height(ages) - closed)) < 1e-6


def test_median_centile_is_lms_m():
    ages, heights = centile_curve("statage", "boy", 0.0)
    table = lms_table("statage", "boy").set_index("age")
    assert np.allclose(heights, table.loc[ages, "M"].to_numpy())


def test_growth_velocity_peaks_in_puberty(boy, girl):
    age_b, v_b = boy.peak_height_velocity()
    age_g, v_g = girl.peak_height_velocity()
    assert 12.5 < age_b < 14.5 and 10.0 < age_g < 12.5
    assert age_g < age_b
