import pytest
import sys
import pandas as pd
from modular_parts.ranking import calculate_prometheeI_ranking

sys.path.append('../..')


@pytest.fixture
def outranking_flows():
    alternatives = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']
    return pd.DataFrame({'positive': [0.04151, 0.12188, 0.26870, 0.60934, 0.26058, 0.03652],
                         'negative': [0.49889, 0.22204, 0.08527, 0.05025, 0.08933, 0.39276]
                         }, index=alternatives)


def test_prometheeI_ranking(outranking_flows):
    expected = [('a1', ' ? ', 'a2'), ('a1', ' ? ', 'a3'), ('a1', ' ? ', 'a4'), ('a1', ' ? ', 'a5'), ('a1', ' ? ', 'a6'),
                ('a2', ' P ', 'a1'), ('a2', ' ? ', 'a3'), ('a2', ' ? ', 'a4'), ('a2', ' ? ', 'a5'), ('a2', ' P ', 'a6'),
                ('a3', ' P ', 'a1'), ('a3', ' P ', 'a2'), ('a3', ' ? ', 'a4'), ('a3', ' P ', 'a5'), ('a3', ' P ', 'a6'),
                ('a4', ' P ', 'a1'), ('a4', ' P ', 'a2'), ('a4', ' P ', 'a3'), ('a4', ' P ', 'a5'), ('a4', ' P ', 'a6'),
                ('a5', ' P ', 'a1'), ('a5', ' P ', 'a2'), ('a5', ' ? ', 'a3'), ('a5', ' ? ', 'a4'), ('a5', ' P ', 'a6'),
                ('a6', ' ? ', 'a1'), ('a6', ' ? ', 'a2'), ('a6', ' ? ', 'a3'), ('a6', ' ? ', 'a4'), ('a6', ' ? ', 'a5')]

    actual = calculate_prometheeI_ranking(outranking_flows, weak_preference=False)

    assert all([e == a for e, a in zip(expected, actual)])


if __name__ == '__main__':
    test_prometheeI_ranking(outranking_flows)
