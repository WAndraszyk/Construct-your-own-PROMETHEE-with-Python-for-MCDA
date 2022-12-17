import pytest
import sys
import pandas as pd
from pandas.testing import assert_series_equal
from modular_parts.alternatives_profiles import\
    calculate_alternatives_profiles

sys.path.append('../..')


@pytest.fixture
def partial_preferences():
    alternatives = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']
    criteria = ['g1', 'g2', 'g3']

    g1_preferences = pd.DataFrame([[0, 0, 0, 0, 0, 0.3],
                                   [1, 0, 1, 1, 1, 1],
                                   [0.75, 0, 0, 0.5, 0.1, 1],
                                   [0.25, 0, 0, 0, 0, 0.5],
                                   [0.65, 0, 0, 0.4, 0, 0.9],
                                   [0, 0, 0, 0, 0, 0]], index=alternatives,
                                  columns=alternatives)

    g2_preferences = pd.DataFrame([[0, 1, 0, 1, 1, 0],
                                   [0, 0, 0, 0, 0, 0],
                                   [0, 1, 0, 1, 1, 0],
                                   [0, 1, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0],
                                   [1, 1, 1, 1, 1, 0]], index=alternatives,
                                  columns=alternatives)

    g3_preferences = pd.DataFrame([[0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0.5],
                                   [0, 0, 0, 0, 0, 0.5],
                                   [0.5, 0, 0, 0, 0, 1],
                                   [0.5, 0.5, 0.5, 0, 0, 1],
                                   [0, 0, 0, 0, 0, 0]], index=alternatives,
                                  columns=alternatives)

    return pd.concat([g1_preferences, g2_preferences, g3_preferences],
                     keys=criteria, names=['criteria', 'alternatives'])


@pytest.fixture
def criteria_weights():
    return pd.Series([2, 0.8, 1.5], index=['g1', 'g2', 'g3'],
                     name='criteria_weights')


def test_promethee_alternatives_profiles(partial_preferences,
                                         criteria_weights):
    alternatives = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']
    expected = pd.Series([-0.92, 1.36, 0.86, -0.33, 0.61, -1.58],
                         index=alternatives)

    actual = calculate_alternatives_profiles(criteria_weights,
                                             partial_preferences)

    assert_series_equal(expected, actual, atol=0.006)


if __name__ == '__main__':
    test_promethee_alternatives_profiles(partial_preferences,
                                         criteria_weights)
