import pytest
import sys
import pandas as pd
from pandas.testing import assert_series_equal, assert_frame_equal
from modular_parts.flows import calculate_net_outranking_flows, \
    calculate_net_outranking_flows_for_prometheeII

sys.path.append('../..')


@pytest.fixture
def flows():
    alternatives = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']
    return pd.DataFrame(
        {'positive': [0.04151, 0.12188, 0.26870, 0.60934, 0.26058, 0.03652],
         'negative': [0.49889, 0.22204, 0.08527, 0.05025, 0.08933, 0.39276]
         }, index=alternatives)


def test_net_outranking_flows(flows):
    alternatives = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']
    expected = pd.Series(
        [-0.45738, -0.10016, 0.18343, 0.55909, 0.17125, -0.35624],
        index=alternatives,
        dtype='float64', name='Net outranking flow')

    actual = calculate_net_outranking_flows(flows)
    assert_series_equal(expected, actual, atol=0.006)


def test__net_outranking_flows_for_prometheeII(flows):
    alternatives = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']
    expected = pd.DataFrame(
        {'positive': [0.04151, 0.12188, 0.26870, 0.60934, 0.26058, 0.03652],
         'negative': [0.49889, 0.22204, 0.08527, 0.05025, 0.08933, 0.39276],
         'net': [-0.45738, -0.10016, 0.18343, 0.55909, 0.17125, -0.35624]
         }, index=alternatives)
    actual = calculate_net_outranking_flows_for_prometheeII(flows)
    assert_frame_equal(expected, actual, atol=0.006)


if __name__ == '__main__':
    test_net_outranking_flows(flows)
    test__net_outranking_flows_for_prometheeII(flows)
