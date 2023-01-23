import pandas as pd
import pytest
from pandas.testing import assert_frame_equal, assert_series_equal

from modular_parts.M9_NetOutrankingFlow import calculate_net_outranking_flows


@pytest.fixture
def flows():
    alternatives = ["a1", "a2", "a3", "a4", "a5", "a6"]
    return pd.DataFrame(
        {
            "positive": [0.04151, 0.12188, 0.26870, 0.60934, 0.26058, 0.03652],
            "negative": [0.49889, 0.22204, 0.08527, 0.05025, 0.08933, 0.39276],
        },
        index=alternatives,
    )


def test_net_outranking_flows(flows):
    alternatives = ["a1", "a2", "a3", "a4", "a5", "a6"]
    expected = pd.Series(
        [-0.45738, -0.10016, 0.18343, 0.55909, 0.17125, -0.35624],
        index=alternatives,
        dtype="float64",
    )

    actual = calculate_net_outranking_flows(flows)
    assert_series_equal(expected, actual, atol=0.006)


def test__net_outranking_flows_for_profile_based(flows):
    alternatives = ["a1", "a2", "a3", "a4", "a5", "a6"]
    expected = pd.DataFrame(
        {
            "positive": [0.04151, 0.12188, 0.26870, 0.60934, 0.26058, 0.03652],
            "negative": [0.49889, 0.22204, 0.08527, 0.05025, 0.08933, 0.39276],
            "net": [-0.45738, -0.10016, 0.18343, 0.55909, 0.17125, -0.35624],
        },
        index=alternatives,
    )
    actual = calculate_net_outranking_flows(flows, True)
    assert_frame_equal(expected, actual, atol=0.006)
