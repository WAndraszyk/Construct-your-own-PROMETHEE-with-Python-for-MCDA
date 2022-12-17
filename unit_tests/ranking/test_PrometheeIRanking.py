import pytest
import sys
import pandas as pd
from modular_parts.ranking import calculate_prometheeI_ranking
from core.enums import RelationType
# from mcda.core.sorting import RelationType -> ścieżka francuza

sys.path.append('../..')


@pytest.fixture
def outranking_flows():
    alternatives = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']
    return pd.DataFrame(
        {'positive': [0.04151, 0.12188, 0.26870, 0.60934, 0.26058, 0.03652],
         'negative': [0.49889, 0.22204, 0.08527, 0.05025, 0.08933, 0.39276]
         }, index=alternatives)


def test_prometheeI_ranking(outranking_flows):
    expected = [
        ('a1', 'a2', RelationType.INCOMPARABLE),
        ('a1', 'a3', RelationType.INCOMPARABLE),
        ('a1', 'a4', RelationType.INCOMPARABLE),
        ('a1', 'a5', RelationType.INCOMPARABLE),
        ('a1', 'a6', RelationType.INCOMPARABLE),
        ('a2', 'a1', RelationType.PREFERENCE),
        ('a2', 'a3', RelationType.INCOMPARABLE),
        ('a2', 'a4', RelationType.INCOMPARABLE),
        ('a2', 'a5', RelationType.INCOMPARABLE),
        ('a2', 'a6', RelationType.PREFERENCE),
        ('a3', 'a1', RelationType.PREFERENCE),
        ('a3', 'a2', RelationType.PREFERENCE),
        ('a3', 'a4', RelationType.INCOMPARABLE),
        ('a3', 'a5', RelationType.PREFERENCE),
        ('a3', 'a6', RelationType.PREFERENCE),
        ('a4', 'a1', RelationType.PREFERENCE),
        ('a4', 'a2', RelationType.PREFERENCE),
        ('a4', 'a3', RelationType.PREFERENCE),
        ('a4', 'a5', RelationType.PREFERENCE),
        ('a4', 'a6', RelationType.PREFERENCE),
        ('a5', 'a1', RelationType.PREFERENCE),
        ('a5', 'a2', RelationType.PREFERENCE),
        ('a5', 'a3', RelationType.INCOMPARABLE),
        ('a5', 'a4', RelationType.INCOMPARABLE),
        ('a5', 'a6', RelationType.PREFERENCE),
        ('a6', 'a1', RelationType.INCOMPARABLE),
        ('a6', 'a2', RelationType.INCOMPARABLE),
        ('a6', 'a3', RelationType.INCOMPARABLE),
        ('a6', 'a4', RelationType.INCOMPARABLE),
        ('a6', 'a5', RelationType.INCOMPARABLE)
    ]

    actual = calculate_prometheeI_ranking(outranking_flows,
                                          weak_preference=False)

    assert actual == expected


if __name__ == '__main__':
    test_prometheeI_ranking(outranking_flows)
