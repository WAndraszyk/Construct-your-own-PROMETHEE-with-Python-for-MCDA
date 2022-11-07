import pytest
import sys
import pandas as pd
from pandas.testing import assert_frame_equal
from modular_parts.ranking import calculate_prometheeI_ranking

sys.path.append('../..')


@pytest.fixture
def outranking_flows():
    alternatives = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']
    return pd.DataFrame({'positive': [0.04151, 0.12188, 0.26870, 0.60934, 0.26058, 0.03652],
                         'negative': [0.49889, 0.22204, 0.08527, 0.05025, 0.08933, 0.39276]
                         }, index=alternatives)


def test_prometheeI_ranking(outranking_flows):
    alternatives = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']
    expected = pd.DataFrame([[None, '?', '?', '?', '?', '?'], ['P', None, '?', '?', '?', 'P'],
                             ['P', 'P', None, '?', 'P', 'P'], ['P', 'P', 'P', None, 'P', 'P'],
                             ['P', 'P', '?', '?', None, 'P'], ['?', '?', '?', '?', '?', None,]],
                            index=alternatives, columns=alternatives)

    actual = calculate_prometheeI_ranking(outranking_flows, weak_preference=False)

    assert_frame_equal(expected, actual, atol=0.006)


if __name__ == '__main__':
    test_prometheeI_ranking(outranking_flows)
