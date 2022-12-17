import pytest
import sys
import pandas as pd
from pandas.testing import assert_series_equal
from modular_parts.sorting import calculate_prometheetri_sorted_alternatives

sys.path.append('../..')


@pytest.fixture
def categories():
    return [f"C{i}" for i in range(1, 4)]


@pytest.fixture
def criteria_weights():
    criteria = [f"g{i}" for i in range(1, 6)]
    return pd.Series([0.283018867924528, 0.188679245283019, 0.188679245283019,
                      0.188679245283019, 0.150943396226415],
                     index=criteria)


@pytest.fixture
def alternatives_partial_preferences():
    alternatives = [f"a{i}" for i in range(1, 13)]
    profiles = [f"p{i}" for i in range(1, 4)]
    criteria = [f"g{i}" for i in range(1, 6)]

    g1_alternatives_profiles_preferences = pd.DataFrame(
        [[1.0, 0.4, 0.0], [0.7, 0.0, 0.0], [0.5, 0.0, 0.0],
         [0.5, 0.0, 0.0], [0.5, 0.0, 0.0], [1.0, 1.0, 0.0],
         [1.0, 0.0, 0.0], [1.0, 0.6, 0.0], [1.0, 1.0, 0.2],
         [0.5, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.2]],
        index=alternatives, columns=profiles)

    g2_alternatives_profiles_preferences = pd.DataFrame(
        [[1.0, 0.3, 0.0], [0.8, 0.0, 0.0], [1.0, 0.2, 0.0],
         [0.0, 0.0, 0.0], [1.0, 1.0, 0.5], [1.0, 0.5, 0.0],
         [0.5, 0.0, 0.0], [1.0, 1.0, 0.0], [1.0, 0.5, 0.0],
         [0.0, 0.0, 0.0], [1.0, 0.5, 0.0], [1.0, 1.0, 0.0]],
        index=alternatives, columns=profiles)

    g3_alternatives_profiles_preferences = pd.DataFrame(
        [[1.0, 0.857142857142857, 0.0], [1.0, 1.0, 0.142857142857143],
         [1.0, 1.0, 0.142857142857143], [0.714285714285714, 0.0, 0.0],
         [1.0, 0.428571428571429, 0.0], [0.0, 0.0, 0.0],
         [1.0, 0.428571428571429, 0.0], [1.0, 1.0, 0.0],
         [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0],
         [1.0, 1.0, 0.0]], index=alternatives, columns=profiles)

    g4_alternatives_profiles_preferences = pd.DataFrame(
        [[1.0, 0.999999999999987, 0.0], [1.0, 1.0, 0.864664716763387],
         [1.0, 0.999999999999987, 0.0], [0.0, 0.0, 0.0],
         [1.0, 1.0, 0.864664716763387], [0.0, 0.0, 0.0],
         [1.0, 0.999999999999987, 0.0], [1.0, 1.0, 0.864664716763387],
         [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0],
         [1.0, 1.0, 0.864664716763387]],
        index=alternatives, columns=profiles)

    g5_alternatives_profiles_preferences = pd.DataFrame(
        [[1.0, 1.0, 0.0], [0.166666666666667, 0.0, 0.0],
         [1.0, 0.166666666666667, 0.0], [1.0, 0.0, 0.0],
         [1.0, 1.0, 0.166666666666667], [1.0, 1.0, 0.0],
         [1.0, 0.166666666666667, 0.0], [1.0, 1.0, 0.0],
         [1.0, 1.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0],
         [1.0, 1.0, 0.0]], index=alternatives, columns=profiles)

    alternatives_vs_profiles_partial_preferences = pd.concat(
        [g1_alternatives_profiles_preferences,
         g2_alternatives_profiles_preferences,
         g3_alternatives_profiles_preferences,
         g4_alternatives_profiles_preferences,
         g5_alternatives_profiles_preferences], keys=criteria)

    g1_profiles_vs_alternatives = pd.DataFrame(
        [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
         [0.0, 0.8, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.5, 0.0],
         [0.6, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0, 0.4, 0.0, 1.0, 1.0, 0.0]],
        index=profiles, columns=alternatives)

    g2_profiles_vs_alternatives = pd.DataFrame(
        [[0.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0],
         [0.0, 0.2, 0.0, 1.0, 0.0, 0.0, 0.5, 0.0, 0.0, 1.0, 0.0, 0.0],
         [0.7, 1.0, 0.8, 1.0, 0.0, 0.5, 1.0, 0.0, 0.5, 1.0, 0.5, 0.0]],
        index=profiles, columns=alternatives)

    g3_profiles_vs_alternatives = pd.DataFrame(
        [[0.0, 0.0, 0.0, 0.0, 0.0, 0.714285714285714, 0.0, 0.0,
          0.714285714285714, 0.0, 0.714285714285714, 0.0],
         [0.0, 0.0, 0.0, 0.285714285714286, 0.0, 1.0, 0.0, 0.0, 1.0,
          1.0, 1.0, 0.0],
         [0.571428571428571, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.285714285714286,
          1.0, 1.0, 1.0, 0.0]],
        index=profiles, columns=alternatives)

    g4_profiles_vs_alternatives = pd.DataFrame(
        [[0.0, 0.0, 0.0, 0.0, 0.0, 0.999999999977103, 0.0, 0.0,
          0.393469340287367, 0.988891003461758, 0.999999999977103, 0.0],
         [0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0],
         [0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0]],
        index=profiles, columns=alternatives)

    g5_profiles_vs_alternatives = pd.DataFrame(
        [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.166666666666667,
          0.0, 0.0],
         [0.0, 0.166666666666667, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0,
          0.0],
         [0.166666666666667, 1.0, 1.0, 1.0, 0.0, 0.166666666666667, 1.0,
          0.166666666666667, 0.0, 1.0, 1.0, 0.0]],
        index=profiles, columns=alternatives)

    profiles_vs_alternatives_partial_preferences = pd.concat(
        [g1_profiles_vs_alternatives, g2_profiles_vs_alternatives,
         g3_profiles_vs_alternatives, g4_profiles_vs_alternatives,
         g5_profiles_vs_alternatives], keys=criteria)

    return alternatives_vs_profiles_partial_preferences, \
        profiles_vs_alternatives_partial_preferences


@pytest.fixture
def profiles_partial_preferences():
    profiles = [f"p{i}" for i in range(1, 4)]
    criteria = [f"g{i}" for i in range(1, 6)]

    g1_profiles_preferences = pd.DataFrame(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0]], index=profiles,
        columns=profiles)

    g2_profiles_preferences = pd.DataFrame(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0]], index=profiles,
        columns=profiles)

    g3_profiles_preferences = pd.DataFrame(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0]], index=profiles,
        columns=profiles)

    g4_profiles_preferences = pd.DataFrame(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0]], index=profiles,
        columns=profiles)

    g5_profiles_preferences = pd.DataFrame(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0]], index=profiles,
        columns=profiles)

    return pd.concat([g1_profiles_preferences, g2_profiles_preferences,
                      g3_profiles_preferences,
                      g4_profiles_preferences, g5_profiles_preferences],
                     keys=criteria)


@pytest.fixture
def assign_to_better_class():
    return True


@pytest.fixture
def use_marginal_value():
    return True


def test_calculate_prometheetri_sorted_alternatives(
        categories,
        criteria_weights,
        alternatives_partial_preferences,
        profiles_partial_preferences,
        assign_to_better_class,
        use_marginal_value):
    alternatives = [f"a{i}" for i in range(1, 13)]
    expected = pd.Series(
        ['C2', 'C2', 'C2', 'C2', 'C2', 'C2', 'C2', 'C3', 'C2', 'C1', 'C1',
         'C3'],
        index=alternatives)
    actual = calculate_prometheetri_sorted_alternatives(
        categories,
        criteria_weights,
        alternatives_partial_preferences,
        profiles_partial_preferences,
        assign_to_better_class,
        use_marginal_value)

    assert_series_equal(expected, actual)


if __name__ == '__main__':
    test_calculate_prometheetri_sorted_alternatives(
        categories,
        criteria_weights,
        alternatives_partial_preferences,
        profiles_partial_preferences,
        assign_to_better_class,
        use_marginal_value)
