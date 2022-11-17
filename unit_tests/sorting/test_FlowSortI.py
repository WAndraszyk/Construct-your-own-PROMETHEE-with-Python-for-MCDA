import pytest
import sys
import pandas as pd
from core.enums import CompareProfiles
from pandas.testing import assert_frame_equal
from modular_parts.sorting import calculate_flowsortI_sorted_alternatives

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
    return pd.DataFrame(
        {'positive': [0.48, 0.20, 0.40],
         'negative': [0.52, 0.80, 0.40]
         }, index=alternatives)


@pytest.fixture
def category_profiles_flows():
    profiles = [f"r{i}" for i in range(1, 6)]
    return pd.DataFrame(
        {'positive': [0.0, 0.4, 0.6, 0.866667, 1.0],
         'negative': [1.0, 0.466667, 0.333333, 0.0, 0.0]
         }, index=profiles)


@pytest.fixture
def comparison_with_profiles():
    return CompareProfiles.LIMITING_PROFILES


def test(categories, category_profiles_performances, criteria_directions, alternatives_flows,
         category_profiles_flows, comparison_with_profiles):
    actual_classification = calculate_flowsortI_sorted_alternatives(categories, category_profiles_performances,
                                                                    criteria_directions, alternatives_flows,
                                                                    category_profiles_flows, comparison_with_profiles)

    expected_classification = pd.DataFrame([[True, True, False, False], [True, False, False, False],
                                            [True, True, False, False]],
                                           index=alternatives_flows.index, columns=categories)

    assert_frame_equal(expected_classification, actual_classification)


if __name__ == '__main__':
    test(categories, category_profiles_performances, criteria_directions, alternatives_flows,
         category_profiles_flows, comparison_with_profiles)
