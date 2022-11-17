import pytest
import sys
import pandas as pd
from core.enums import CompareProfiles
from pandas.testing import assert_series_equal
from modular_parts.sorting import calculate_flowsortII_sorted_alternatives

sys.path.append('../..')


@pytest.fixture
def categories():
    return [f"c{i}" for i in range(1, 5)]


@pytest.fixture
def category_profiles_performances():
    profiles = [f"r{i}" for i in range(1, 6)]
    criteria = [f"g{i}" for i in range(1, 6)]
    return pd.DataFrame([[0, 0, 0, 0, 0], [25, 25, 25, 25, 25], [50, 50, 50, 50, 50],
                         [75, 75, 75, 75, 75], [100, 100, 100, 100, 100]],
                        index=profiles, columns=criteria)


@pytest.fixture
def criteria_directions():
    criteria = [f"g{i}" for i in range(1, 6)]
    return pd.Series([1, 1, 1, 1, 1], index=criteria)


@pytest.fixture
def alternatives_flows():
    alternatives = [f"a{i}" for i in range(1, 4)]
    return pd.Series([-0.04, -0.60, -0.00], index=alternatives)


@pytest.fixture
def category_profiles_flows():
    profiles = [f"r{i}" for i in range(1, 6)]
    return pd.Series([-1.000000, -0.066667, 0.266667, 0.866667, 1.000000], index=profiles)


@pytest.fixture
def comparison_with_profiles():
    return CompareProfiles.LIMITING_PROFILES


def test_flowsort_ii(categories, category_profiles_performances, criteria_directions, alternatives_flows,
                     category_profiles_flows, comparison_with_profiles):
    actual_classification = calculate_flowsortII_sorted_alternatives(categories, category_profiles_performances,
                                                                     criteria_directions, alternatives_flows,
                                                                     category_profiles_flows, comparison_with_profiles)

    expected_classification = pd.Series(['c2', 'c1', 'c2'], index=alternatives_flows.index)
    assert_series_equal(expected_classification, actual_classification)


if __name__ == '__main__':
    test_flowsort_ii(categories, category_profiles_performances, criteria_directions, alternatives_flows,
                     category_profiles_flows, comparison_with_profiles)
