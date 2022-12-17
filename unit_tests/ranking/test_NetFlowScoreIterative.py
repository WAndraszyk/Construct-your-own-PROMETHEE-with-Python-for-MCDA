import pytest
import sys
import pandas as pd
from pandas.testing import assert_series_equal
from core.enums import ScoringFunction, ScoringFunctionDirection
from modular_parts.ranking import calculate_netflow_score_ranking

sys.path.append('../..')


@pytest.fixture
def alternatives_preferences():
    alternatives = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']
    return pd.DataFrame([[0, 0.06554, 0.02185, 0.07647, 0, 0.04370],
                         [0.36323, 0, 0, 0.01092, 0, 0.23526],
                         [0.5586, 0.23632, 0, 0.05462, 0.04697, 0.44973],
                         [0.92353, 0.56030, 0.36767, 0, 0.39967, 0.79555],
                         [0.52386, 0.22617, 0.03683, 0.07647, 0, 0.43958],
                         [0.12798, 0.02185, 0, 0.03277, 0, 0]],
                        index=alternatives, columns=alternatives)


def test_net_flow_score_sum_favor(alternatives_preferences):
    alternatives = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']
    net_flow_score = pd.Series(
        [0.20756, 0.60941, 1.34624, 3.04672, 1.30291, 0.1826],
        index=alternatives)
    expected = net_flow_score.sort_values(ascending=False)
    actual = calculate_netflow_score_ranking(
        alternatives_preferences,
        ScoringFunction.SUM,
        ScoringFunctionDirection.IN_FAVOR)

    assert_series_equal(expected, actual, atol=0.006)


def test_net_flow_score_min_against(alternatives_preferences):
    alternatives = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']
    net_flow_score = pd.Series(
        [-0.12798, -0.02185, -0.03683, -0.01092, -0.04697, -0.04370],
        index=alternatives)
    expected = net_flow_score.sort_values(ascending=False)
    actual = calculate_netflow_score_ranking(alternatives_preferences,
                                             ScoringFunction.MIN,
                                             ScoringFunctionDirection.AGAINST)

    assert_series_equal(expected, actual, atol=0.006)


def test_net_flow_score_max_difference(alternatives_preferences):
    alternatives = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']
    net_flow_score = pd.Series(
        [-0.08428, 0.29769, 0.53675, 0.84706, 0.52386, 0.08428],
        index=alternatives)
    expected = net_flow_score.sort_values(ascending=False)
    actual = calculate_netflow_score_ranking(
        alternatives_preferences,
        ScoringFunction.MAX,
        ScoringFunctionDirection.DIFFERENCE)

    assert_series_equal(expected, actual, atol=0.006)


if __name__ == '__main__':
    test_net_flow_score_sum_favor(alternatives_preferences)
    test_net_flow_score_min_against(alternatives_preferences)
    test_net_flow_score_max_difference(alternatives_preferences)
