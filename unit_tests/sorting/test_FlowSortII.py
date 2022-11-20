import pytest
import sys
import pandas as pd
from core.enums import CompareProfiles
from pandas.testing import assert_frame_equal
from modular_parts.sorting import calculate_flowsortII_sorted_alternatives

sys.path.append('../..')


@pytest.fixture
def categories_limiting():
    return [f"C{i}" for i in range(1, 5)]


@pytest.fixture
def categories_central():
    return [f"C{i}" for i in range(1, 5)]


@pytest.fixture
def category_profiles_performances_limiting():
    profiles = [f"r{i}" for i in range(1, 6)]
    criteria = [f"g{i}" for i in range(1, 6)]
    return pd.DataFrame([[0, 0, 0, 0, 0], [25, 25, 25, 25, 25], [50, 50, 50, 50, 50],
                         [75, 75, 75, 75, 75], [100, 100, 100, 100, 100]],
                        index=profiles, columns=criteria)


@pytest.fixture
def category_profiles_performances_central():
    profiles = [f"r{i}" for i in range(1, 5)]
    criteria = [f"g{i}" for i in range(1, 6)]
    return pd.DataFrame([[10, 5, 10, 10, 15], [40, 35, 35, 30, 33], [56, 62, 58, 61, 52],
                         [80, 90, 90, 75, 82]],
                        index=profiles, columns=criteria)


@pytest.fixture
def criteria_directions():
    criteria = [f"g{i}" for i in range(1, 6)]
    return pd.Series([1, 1, 1, 1, 1], index=criteria)


@pytest.fixture
def prometheeII_flows_limiting():
    alternatives = [f"a{i}" for i in range(1, 4)]
    profiles = [f"p{i}" for i in range(1, 6)]
    external_index = []
    internal_index = []
    for alternative in alternatives:
        external_index += [f"R{alternative}"] * (len(profiles) + 1)
        internal_index += profiles + [alternative]

    flows_index = pd.MultiIndex.from_arrays([external_index, internal_index])

    return pd.DataFrame({'positive': [0.0, 0.24, 0.48, 0.8, 1.0, 0.48,
                                      0.0, 0.4, 0.6, 0.8, 1.0, 0.2,
                                      0.0, 0.2, 0.48, 0.72, 1.0, 0.4],
                         'negative': [1.0, 0.76, 0.52, 0.2, 0.0, 0.52,
                                      1.0, 0.6, 0.4, 0.2, 0.0, 0.8,
                                      1.0, 0.72, 0.48, 0.2, 0.0, 0.4],
                         'net': [-1.0, -0.48, -0.14, 0.6, 1.0, -0.14,
                                 -1.0, -0.2, 0.2, 0.6, 1.0, -0.6,
                                 -1.0, -0.52, -0.14, 0.52, 1.0, 0.0]},
                        index=flows_index)


@pytest.fixture
def prometheeII_flows_central():
    alternatives = [f"a{i}" for i in range(1, 4)]
    profiles = [f"p{i}" for i in range(1, 5)]
    external_index = []
    internal_index = []
    for alternative in alternatives:
        external_index += [f"R{alternative}"] * (len(profiles) + 1)
        internal_index += profiles + [alternative]

    flows_index = pd.MultiIndex.from_arrays([external_index, internal_index])

    return pd.DataFrame({'positive': [0.0, 0.3, 0.6, 1, 0.54,
                                      0.0, 0.49, 0.75, 1.0, 0.09,
                                      0.0, 0.33, 0.65, 0.92, 0.5],
                         'negative': [0.99, 0.7, 0.34, 0.0, 0.4,
                                      0.84, 0.5, 0.25, 0.0, 0.74,
                                      1.0, 0.65, 0.35, 0.0, 0.4],
                         'net': [-0.99, -0.4, -0.26, 1.0, 0.14,
                                 -0.84, -0.01, 0.5, 1.0, -0.65,
                                 -1.0, -0.32, 0.3, 0.92, 0.1]},
                        index=flows_index)


def test_flowsortII_limiting(categories_limiting, category_profiles_performances_limiting, criteria_directions,
                             prometheeII_flows_limiting):
    actual_classification = calculate_flowsortII_sorted_alternatives(categories_limiting,
                                                                     category_profiles_performances_limiting,
                                                                     criteria_directions, prometheeII_flows_limiting,
                                                                     CompareProfiles.LIMITING_PROFILES)

    alternatives = [f"a{i}" for i in range(1, 4)]
    expected_classification = pd.DataFrame({'positive': ['C2', 'C1', 'C2'],
                                            'negative': ['C2', 'C1', 'C3'],
                                            'net': ['C2', 'C1', 'C3']}, index=alternatives)
    assert_frame_equal(actual_classification, expected_classification)


def test_flowsortII_central(categories_central, category_profiles_performances_central, criteria_directions,
                            prometheeII_flows_central):
    actual_classification = calculate_flowsortII_sorted_alternatives(categories_central,
                                                                     category_profiles_performances_central,
                                                                     criteria_directions, prometheeII_flows_central,
                                                                     CompareProfiles.CENTRAL_PROFILES)

    alternatives = [f"a{i}" for i in range(1, 4)]
    expected_classification = pd.DataFrame({'positive': ['C3', 'C1', 'C3'],
                                            'negative': ['C3', 'C1', 'C3'],
                                            'net': ['C3', 'C1', 'C3']}, index=alternatives)
    assert_frame_equal(actual_classification, expected_classification)


if __name__ == '__main__':
    test_flowsortII_limiting(categories_limiting, category_profiles_performances_limiting, criteria_directions,
                             prometheeII_flows_limiting)
    test_flowsortII_central(categories_central, category_profiles_performances_central, criteria_directions,
                            prometheeII_flows_central)
