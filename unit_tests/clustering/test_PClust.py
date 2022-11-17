import pytest
import sys
import pandas as pd
from core.enums import PreferenceFunction
from pandas.testing import assert_frame_equal
from modular_parts.clustering import cluster_using_pclust

sys.path.append('../..')


@pytest.fixture
def alternatives_performances():
    alternatives = [f"a{i}" for i in range(1, 13)]
    criteria = [f"g{i}" for i in range(1, 6)]
    return pd.DataFrame([[84.0, 83.0, 12.0, 7.0, 85.0], [72.0, 78.0, 7.0, 5.0, 70.0], [70.0, 82.0, 7.0, 7.0, 80.0],
                         [70.0, 68.0, 20.0, 25.0, 75.0], [70.0, 95.0, 15.0, 5.0, 95.0], [90.0, 85.0, 30.0, 32.0, 85.0],
                         [80.0, 75.0, 15.0, 7.0, 80.0], [86.0, 90.0, 10.0, 5.0, 85.0], [92.0, 85.0, 30.0, 26.0, 90.0],
                         [70.0, 65.0, 25.0, 28.0, 60.0], [75.0, 85.0, 30.0, 32.0, 65.0], [92.0, 90.0, 8.0, 5.0, 90.0]],
                        index=alternatives, columns=criteria)


@pytest.fixture
def preference_thresholds():
    criteria = [f"g{i}" for i in range(1, 6)]
    return pd.Series([10, 10, 7, 0, 10], index=criteria)


@pytest.fixture
def indifference_thresholds():
    criteria = [f"g{i}" for i in range(1, 6)]
    return pd.Series([0, 0, 0, 0, 4], index=criteria)


@pytest.fixture
def standard_deviations():
    criteria = [f"g{i}" for i in range(1, 6)]
    return pd.Series([0, 0, 0, 1, 0], index=criteria)


@pytest.fixture
def generalized_criteria():
    criteria = [f"g{i}" for i in range(1, 6)]
    return pd.Series([PreferenceFunction.V_SHAPE,
                      PreferenceFunction.V_SHAPE,
                      PreferenceFunction.V_SHAPE,
                      PreferenceFunction.GAUSSIAN,
                      PreferenceFunction.V_SHAPE_INDIFFERENCE], index=criteria)


@pytest.fixture
def criteria_directions():
    criteria = [f"g{i}" for i in range(1, 6)]
    return pd.Series([1, 1, 0, 0, 1], index=criteria)


@pytest.fixture
def criteria_weights():
    criteria = [f"g{i}" for i in range(1, 6)]
    return pd.Series([0.283018867924528, 0.188679245283019, 0.188679245283019, 0.188679245283019, 0.150943396226415],
                     index=criteria)


@pytest.fixture
def n_categories():
    return 3


@pytest.fixture
def alternatives_flows():
    alternatives = [f"a{i}" for i in range(1, 13)]
    return pd.DataFrame([[0.466103079310626, 0.230034988326492],
                         [0.348422671858281, 0.371926815323042],
                         [0.3245119660214, 0.341486429966613],
                         [0.156603420091293, 0.65600751449808],
                         [0.510719494532462, 0.243445234011272],
                         [0.337335620354488, 0.383887082385448],
                         [0.375602385036347, 0.415120343223168],
                         [0.599913319575344, 0.0876419178305971],
                         [0.431640903710179, 0.31288316274282],
                         [0.0710495063053403, 0.772747423119111],
                         [0.133504859919954, 0.62002201663359],
                         [0.695559811448251, 0.0157641101037327]],
                        index=alternatives, columns=['positive', 'negative'])


def test_calculate_alternatives_support(alternatives_performances, preference_thresholds, indifference_thresholds,
                                        standard_deviations, generalized_criteria, criteria_directions,
                                        criteria_weights, n_categories, alternatives_flows):
    actual_assigments, actual_central_profiles, actual_global_quality_index = cluster_using_pclust(
        alternatives_performances, preference_thresholds, indifference_thresholds, standard_deviations,
        generalized_criteria, criteria_directions, criteria_weights, n_categories, alternatives_flows)

    print(actual_assigments)
    print(actual_central_profiles)
    print(actual_global_quality_index)


if __name__ == '__main__':
    test_calculate_alternatives_support(alternatives_performances, preference_thresholds, indifference_thresholds,
                                        standard_deviations, generalized_criteria, criteria_directions,
                                        criteria_weights, n_categories, alternatives_flows)
