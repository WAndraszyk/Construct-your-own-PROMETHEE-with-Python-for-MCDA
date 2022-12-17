import pytest
import sys
import pandas as pd
from pandas.testing import assert_series_equal
from core.enums import GeneralCriterion, Direction
from modular_parts.clustering import promethee_cluster

sys.path.append('../..')


@pytest.fixture
def alternatives_performances():
    alternatives = [f"a{i}" for i in range(1, 13)]
    criteria = [f"g{i}" for i in range(1, 6)]
    return pd.DataFrame(
        [[100.0, 100.0, 0.0, 0.0, 100.0], [0.0, 0.0, 100.0, 100.0, 0.0],
         [70.0, 82.0, 7.0, 7.0, 80.0],
         [70.0, 68.0, 20.0, 25.0, 75.0], [70.0, 95.0, 15.0, 5.0, 95.0],
         [90.0, 85.0, 30.0, 32.0, 85.0],
         [80.0, 75.0, 15.0, 7.0, 80.0], [86.0, 90.0, 10.0, 5.0, 85.0],
         [92.0, 85.0, 30.0, 26.0, 90.0],
         [70.0, 65.0, 25.0, 28.0, 60.0], [75.0, 85.0, 30.0, 32.0, 65.0],
         [92.0, 90.0, 8.0, 5.0, 90.0]],
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
    return pd.Series([GeneralCriterion.V_SHAPE,
                      GeneralCriterion.V_SHAPE,
                      GeneralCriterion.V_SHAPE,
                      GeneralCriterion.GAUSSIAN,
                      GeneralCriterion.V_SHAPE_INDIFFERENCE], index=criteria)


@pytest.fixture
def criteria_directions():
    criteria = [f"g{i}" for i in range(1, 6)]
    return pd.Series(
        [Direction.MAX, Direction.MAX, Direction.MIN, Direction.MIN,
         Direction.MAX], index=criteria)


@pytest.fixture
def criteria_weights():
    criteria = [f"g{i}" for i in range(1, 6)]
    return pd.Series([0.283018867924528, 0.188679245283019, 0.188679245283019,
                      0.188679245283019, 0.150943396226415],
                     index=criteria)


@pytest.fixture
def n_categories(alternatives_performances):
    # return alternatives_performances.values.__len__()
    return 2


def test_cluster_using_promethee_cluster(alternatives_performances,
                                         preference_thresholds,
                                         indifference_thresholds,
                                         standard_deviations,
                                         generalized_criteria,
                                         criteria_directions,
                                         criteria_weights, n_categories):
    assignment = promethee_cluster(alternatives_performances,
                                   preference_thresholds,
                                   indifference_thresholds,
                                   standard_deviations, generalized_criteria,
                                   criteria_directions, criteria_weights,
                                   n_categories)
    assignment_list = []
    for c1, c2 in assignment.items():
        assignment_list.append(c2[0])
    assignment_list.sort()
    assignment_to_test = pd.Series(data=['a1', 'a2'])
    assignment_to_check = pd.Series(data=assignment_list)
    assert_series_equal(assignment_to_check, assignment_to_test, atol=0.006)


if __name__ == '__main__':
    test_cluster_using_promethee_cluster(alternatives_performances,
                                         preference_thresholds,
                                         indifference_thresholds,
                                         standard_deviations,
                                         generalized_criteria,
                                         criteria_directions,
                                         criteria_weights, n_categories)
