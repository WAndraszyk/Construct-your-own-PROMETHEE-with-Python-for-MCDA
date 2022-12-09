import pytest
import sys
import pandas as pd
from pandas.testing import assert_series_equal
from modular_parts.flows import calculate_promethee_group_ranking

sys.path.append('../..')


@pytest.fixture
def dms_flows():
    alternatives = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']
    return pd.DataFrame({'DM1': [-0.40, 0.23, 0.06, -0.19, 0.28, 0.02],
                         'DM2': [0.21, 0.10, -0.19, 0.37, -0.21, -0.29],
                         'DM3': [0.28, 0.28, -0.25, -0.05, -0.42, 0.17],
                         'DM4': [-0.16, 0.09, 0.38, -0.20, -0.11, -0.01]},
                        index=alternatives)


@pytest.fixture
def dms_weights():
    return pd.Series([1, 2, 1, 3], index=['DM1', 'DM2', 'DM3', 'DM4'])


def test_promethee_group_ranking(dms_flows, dms_weights):
    alternatives = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']
    expected = pd.Series([-0.18, 0.98, 0.57, -0.1, -0.89, -0.42],
                         index=alternatives)
    expected.name = 'aggregated_flows'

    actual = calculate_promethee_group_ranking(dms_flows, dms_weights)

    assert_series_equal(expected, actual, atol=0.006)


if __name__ == '__main__':
    test_promethee_group_ranking(dms_flows, dms_weights)
