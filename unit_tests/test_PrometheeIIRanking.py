import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from modular_parts.M15_PrometheeIIRanking import calculate_promethee_ii_ranking


@pytest.fixture
def net_outranking_flows():
    alternatives = ["a1", "a2", "a3", "a4", "a5", "a6"]
    return pd.DataFrame(
        {
            "positive": [
                0.14151,
                0.62188,
                -0.16870,
                0.70934,
                0.36058,
                -0.63652,
            ],
            "negative": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
            "net": [0.04151, 0.52188, -0.26870, 0.60934, 0.26058, -0.73652],
        },
        index=alternatives,
    )


@pytest.fixture
def net_outranking_flows_series():
    alternatives = ["a1", "a2", "a3", "a4", "a5", "a6"]
    return pd.Series(
        [0.04151, 0.52188, -0.26870, 0.60934, 0.26058, -0.73652],
        index=alternatives,
    )


def test_prometheeII_ranking(net_outranking_flows, net_outranking_flows_series):
    expected = pd.Series(
        data=["a4", "a2", "a5", "a1", "a3", "a6"],
        index=[1, 2, 3, 4, 5, 6],
        name="ranking",
    )
    actual = calculate_promethee_ii_ranking(net_outranking_flows)
    assert_series_equal(expected, actual)


def test_prometheeII_ranking_series(net_outranking_flows_series):
    expected = pd.Series(
        data=["a4", "a2", "a5", "a1", "a3", "a6"],
        index=[1, 2, 3, 4, 5, 6],
        name="ranking",
    )

    actual_series = calculate_promethee_ii_ranking(net_outranking_flows_series)
    assert_series_equal(expected, actual_series)
