import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from modular_parts.preference import compute_preference_indices
from core.enums import SurrogateMethod, GeneralCriterion, Direction
from modular_parts.weights import surrogate_weights


@pytest.fixture
def criteria():
    return ['g1', 'g2', 'g3', 'g4', 'g5', 'g6']


@pytest.fixture
def alternatives():
    return ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']


@pytest.fixture
def alternatives_performances(alternatives, criteria):
    performances = [
        [80, 90, 6, 5.4, 8, 5],
        [65, 58, 2, 9.7, 1, 1],
        [83, 60, 4, 7.2, 4, 7],
        [40, 80, 10, 7.5, 7, 10],
        [52, 72, 6, 2.0, 3, 8],
        [94, 96, 7, 3.6, 5, 6]
    ]
    return pd.DataFrame(data=performances, index=alternatives,
                        columns=criteria)


@pytest.fixture
def indifference_thresholds(criteria):
    indifference_thresholds = [10, None, 0.5, 1, None, None]
    return pd.Series(data=indifference_thresholds, index=criteria)


@pytest.fixture
def preference_thresholds(criteria):
    preference_thresholds = [None, 30, 5, 6, None, None]
    return pd.Series(data=preference_thresholds, index=criteria)


@pytest.fixture
def standard_deviations(criteria):
    standard_deviations = [None, None, None, None, None, 5]
    return pd.Series(data=standard_deviations, index=criteria)


@pytest.fixture
def generalized_criteria(criteria):
    generalized_criterion = [GeneralCriterion.U_SHAPE,
                             GeneralCriterion.V_SHAPE,
                             GeneralCriterion.V_SHAPE_INDIFFERENCE,
                             GeneralCriterion.LEVEL, GeneralCriterion.USUAL,
                             GeneralCriterion.GAUSSIAN]
    return pd.Series(data=generalized_criterion, index=criteria)


@pytest.fixture
def criteria_directions(criteria):
    criteria_directions = [Direction.MIN, Direction.MAX, Direction.MIN,
                           Direction.MIN, Direction.MIN, Direction.MAX]
    return pd.Series(data=criteria_directions, index=criteria)


@pytest.fixture
def weights(criteria):
    return surrogate_weights(
        pd.Series(data=[7, 1, 3, 2, 4, 5], index=criteria),
        SurrogateMethod.EW)


def test_preference(criteria, alternatives, alternatives_performances,
                    preference_thresholds, weights,
                    indifference_thresholds, standard_deviations,
                    generalized_criteria, criteria_directions):
    expected = pd.DataFrame(data=[[0.000, 0.296, 0.250, 0.268, 0.100, 0.185],
                                  [0.462, 0.000, 0.389, 0.333, 0.296, 0.500],
                                  [0.236, 0.180, 0.000, 0.333, 0.056, 0.429],
                                  [0.399, 0.505, 0.305, 0.000, 0.223, 0.212],
                                  [0.444, 0.515, 0.487, 0.380, 0.000, 0.448],
                                  [0.286, 0.399, 0.250, 0.432, 0.133, 0.000]],
                            columns=alternatives, index=alternatives)

    actual, _ = compute_preference_indices(alternatives_performances,
                                           preference_thresholds,
                                           indifference_thresholds,
                                           standard_deviations,
                                           generalized_criteria,
                                           criteria_directions, weights)

    assert_frame_equal(actual, expected, atol=0.006)


if __name__ == '__main__':
    test_preference(criteria, alternatives, alternatives_performances,
                    preference_thresholds, weights,
                    indifference_thresholds, standard_deviations,
                    generalized_criteria, criteria_directions)
