import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from modular_parts.preference import compute_preference_indices_with_integrations, compute_preference_indices
from core.enums import PreferenceFunction, Direction, InteractionType


@pytest.fixture
def alternatives():
    return ['a1', 'a2', 'a3', 'a4', 'a5']


@pytest.fixture
def criteria():
    return ['G1', 'G2', 'G3']


@pytest.fixture
def alternatives_performances(alternatives, criteria):
    perf = [[13, 12, 12],  # a1
            [11, 14, 14],  # a2
            [1, 20, 14],
            [14, 40, 40],
            [5, 20, 45]]
    return pd.DataFrame(data=perf, index=alternatives, columns=criteria)


@pytest.fixture
def preference_thresholds(criteria):
    preference_thresholds = [None, 1, 2]
    return pd.Series(data=preference_thresholds, index=criteria)


@pytest.fixture
def indifference_thresholds(criteria):
    indifference_thresholds = [0.4, None, None]
    return pd.Series(data=indifference_thresholds, index=criteria)


@pytest.fixture
def standard_deviations(criteria):
    standard_deviations = [None, None, None]
    return pd.Series(data=standard_deviations, index=criteria)


@pytest.fixture
def generalized_criteria(criteria):
    generalized_criteria_list = [PreferenceFunction.U_SHAPE, PreferenceFunction.V_SHAPE, PreferenceFunction.V_SHAPE]
    return pd.Series(data=generalized_criteria_list, index=criteria)


@pytest.fixture
def weights(criteria):
    weights = [0.333, 0.500, 0.167]
    return pd.Series(data=weights, index=criteria)


@pytest.fixture
def directions(criteria):
    directions = [Direction.MIN, Direction.MAX, Direction.MAX]
    return pd.Series(data=directions, index=criteria)


@pytest.fixture
def interactions():
    return pd.DataFrame(data=[['G2', 'G3', InteractionType.STN, 0.15],
                              ['G1', 'G2', InteractionType.ANT, 0.10],
                              ['G1', 'G2', InteractionType.WKN, -0.05]],
                        columns=['criterion_1', 'criterion_2', 'type', 'coefficient'])


def test_interactions_preference(alternatives, alternatives_performances, preference_thresholds,
                                 indifference_thresholds, standard_deviations, directions,
                                 generalized_criteria, weights, interactions):
    data = [[0.00, 0.000, 0.000, 0.259, 0.000],
            [1.00, 0.000, 0.000, 0.259, 0.000],
            [1.00, 0.824, 0.000, 0.259, 0.333],
            [0.71, 0.710, 0.710, 0.000, 0.500],
            [1.00, 1.000, 0.167, 0.444, 0.000]]
    expected = pd.DataFrame(data=data, columns=alternatives, index=alternatives)
    actual, _ = compute_preference_indices_with_integrations(alternatives_performances=alternatives_performances,
                                                             preference_thresholds=preference_thresholds,
                                                             indifference_thresholds=indifference_thresholds,
                                                             standard_deviations=standard_deviations,
                                                             generalized_criteria=generalized_criteria,
                                                             directions=directions,
                                                             weights=weights, interactions=interactions)

    assert_frame_equal(actual, expected, atol=0.006)


if __name__ == '__main__':
    test_interactions_preference(alternatives_performances=alternatives_performances,
                                 preference_thresholds=preference_thresholds,
                                 indifference_thresholds=indifference_thresholds,
                                 standard_deviations=standard_deviations,
                                 generalized_criteria=generalized_criteria,
                                 directions=directions, alternatives=alternatives,
                                 weights=weights, interactions=interactions)
