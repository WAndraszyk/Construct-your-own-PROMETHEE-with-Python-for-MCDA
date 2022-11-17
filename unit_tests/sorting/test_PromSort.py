import pytest
import sys
import pandas as pd
from pandas.testing import assert_series_equal, assert_frame_equal
from modular_parts.sorting import calculate_promsort_sorted_alternatives

sys.path.append('../..')


@pytest.fixture
def categories():
    return [f"C{i}" for i in range(1, 5)]


@pytest.fixture
def alternatives_flows():
    alternatives = [f"a{i}" for i in range(1, 13)]
    return pd.DataFrame(
        {'positive': [0.557053009883198, 0.439676427229803, 0.441898772087451, 0.14240790655885,
                      0.583432042683531, 0.383647798742138, 0.400119796346211, 0.68331224633732,
                      0.40251572327044, 0.0471698113207547, 0.188679245283019, 0.739916019922226],
         'negative': [0.144953578915843, 0.30398322851153, 0.289308176100629, 0.584007187780773,
                      0.251572327044025, 0.399221323748186, 0.30188679245283, 0.0640910452231207,
                      0.352688997142961, 0.768693354515415, 0.632973944293259, 0.0]
         }, index=alternatives)


@pytest.fixture
def category_profiles_flows():
    profiles = [f"p{i}" for i in range(1, 4)]
    return pd.DataFrame(
        {'positive': [0.0999772141492737, 0.340708295896975, 0.582659478885894],
         'negative': [0.721660676849356, 0.452530697813716, 0.078265825253163]
         }, index=profiles)


@pytest.fixture
def criteria_thresholds():
    criteria = [f"c{i}" for i in range(1, 6)]
    return pd.Series([0, 0, 0, 0, 0.5], index=criteria)


@pytest.fixture
def category_profiles_performances():
    profiles = [f"p{i}" for i in range(1, 4)]
    criteria = [f"c{i}" for i in range(1, 6)]
    return pd.DataFrame([[65, 70, 25, 25, 65], [80, 80, 18, 15, 75], [90, 90, 8, 7, 90]],
                        index=profiles, columns=criteria)


@pytest.fixture
def criteria_directions():
    criteria = [f"c{i}" for i in range(1, 6)]
    return pd.Series([1, 1, 0, 0, 1], index=criteria)


@pytest.fixture
def cut_point():
    return 0


@pytest.fixture
def assign_to_better_class():
    return True


def test_calculate_promsort_sorted_alternatives(categories, alternatives_flows, category_profiles_flows,
                                                criteria_thresholds, category_profiles_performances,
                                                criteria_directions, cut_point, assign_to_better_class):
    alternatives = [f"a{i}" for i in range(1, 13)]
    expected_first_assigments = pd.DataFrame(
        {'worse': ['C3', 'C3', 'C3', 'C2', 'C3', 'C3', 'C3', 'C4', 'C3', 'C1', 'C2', 'C4'],
         'better': ['C3', 'C3', 'C3', 'C2', 'C3', 'C3', 'C3', 'C4', 'C3', 'C1', 'C2', 'C4']}, index=alternatives)
    expected_final_assigments = pd.Series(['C3', 'C3', 'C3', 'C2', 'C3', 'C3', 'C3', 'C4', 'C3', 'C1', 'C2', 'C4'],
                                          index=alternatives)

    actual_first_assigments, actual_final_assigments = \
        calculate_promsort_sorted_alternatives(categories, alternatives_flows, category_profiles_flows, criteria_thresholds,
                                               category_profiles_performances, criteria_directions,
                                               cut_point, assign_to_better_class)

    assert_frame_equal(expected_first_assigments, actual_first_assigments)
    assert_series_equal(expected_final_assigments, actual_final_assigments)


if __name__ == '__main__':
    test_calculate_promsort_sorted_alternatives(categories, alternatives_flows, category_profiles_flows,
                                                criteria_thresholds, category_profiles_performances,
                                                criteria_directions, cut_point, assign_to_better_class)
