import pytest
import sys
import pandas as pd
from pandas.testing import assert_series_equal

from core.enums import PreferenceFunction, Direction, SurrogateMethod
from modular_parts.clustering import promethee_II_ordered_clustering
from modular_parts.weights import surrogate_weights

sys.path.append('../..')


@pytest.fixture
def alternatives_performances():
    alternatives = [f"a{i}" for i in range(1, 7)]
    criteria = [f"g{i}" for i in range(1, 7)]
    return pd.DataFrame([
        [80, 90, 6, 5.4, 8, 5],
        [65, 58, 2, 9.7, 1, 1],
        [83, 60, 4, 7.2, 4, 7],
        [40, 80, 10, 7.5, 7, 10],
        [52, 72, 6, 2.0, 3, 8],
        [94, 96, 7, 3.6, 5, 6]],
        index=alternatives, columns=criteria)


@pytest.fixture
def preference_thresholds():
    criteria = [f"g{i}" for i in range(1, 7)]
    return pd.Series([0, 30, 5, 6, 0, 0], index=criteria)


@pytest.fixture
def indifference_thresholds():
    criteria = [f"g{i}" for i in range(1, 7)]
    return pd.Series([10, 0, 0.5, 1, 0, 0], index=criteria)


@pytest.fixture
def standard_deviations():
    criteria = [f"g{i}" for i in range(1, 7)]
    return pd.Series([0, 0, 0, 0, 0, 5], index=criteria)


@pytest.fixture
def generalized_criteria():
    criteria = [f"g{i}" for i in range(1, 7)]
    return pd.Series([PreferenceFunction.U_SHAPE, PreferenceFunction.V_SHAPE,
                      PreferenceFunction.V_SHAPE_INDIFFERENCE,
                      PreferenceFunction.LEVEL, PreferenceFunction.USUAL,
                      PreferenceFunction.GAUSSIAN], index=criteria)


@pytest.fixture
def criteria_directions():
    criteria = [f"g{i}" for i in range(1, 7)]
    return pd.Series([Direction.MIN, Direction.MAX, Direction.MIN, Direction.MIN, Direction.MIN, Direction.MAX],
                     index=criteria)


@pytest.fixture
def criteria_weights():
    criteria = [f"g{i}" for i in range(1, 7)]
    return surrogate_weights(pd.Series(data=[7, 1, 3, 2, 4, 5], index=criteria), SurrogateMethod.EW)


@pytest.fixture
def n_categories():
    return 2


def test_cluster_using_prometheecluster(alternatives_performances, preference_thresholds, indifference_thresholds,
                                        standard_deviations, generalized_criteria, criteria_directions,
                                        criteria_weights, n_categories):
    assignment = promethee_II_ordered_clustering(alternatives_performances, preference_thresholds,
                                                 indifference_thresholds,
                                                 standard_deviations, generalized_criteria, criteria_directions,
                                                 criteria_weights, n_categories)
    assignment_to_check = pd.Series(data=[['a2', 'a5'], ['a1', 'a3', 'a4', 'a6']], index=['C1', 'C2'])
    assert_series_equal(assignment_to_check, assignment, atol=0.006)


if __name__ == '__main__':
    test_cluster_using_prometheecluster(alternatives_performances, preference_thresholds, indifference_thresholds,
                                        standard_deviations, generalized_criteria, criteria_directions,
                                        criteria_weights, n_categories)
