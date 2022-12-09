import pytest
import pandas as pd
from pandas.testing import assert_series_equal
from modular_parts.clustering import group_into_ordered_clusters


@pytest.fixture
def preferences():
    alternatives = ['a', 'b', 'c', 'd']
    return pd.DataFrame([[0, 1.05, 1.04, 1.03],
                         [0, 0.00, 0.51, 1.02],
                         [0, 0.50, 0.00, 1.01],
                         [0, 0.00, 0.00, 0.00]], index=alternatives, columns=alternatives)


def test_ordered_clusters(preferences):
    expected = pd.Series([['a'], ['b', 'c'], ['d']], name="Alternatives in clusters", index=[1, 2, 3])
    actual = group_into_ordered_clusters(preferences, 3)
    assert_series_equal(expected, actual)


if __name__ == '__main__':
    test_ordered_clusters(preferences)
