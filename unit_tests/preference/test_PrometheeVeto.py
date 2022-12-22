import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from modular_parts.preference import compute_veto, compute_preference_indices
from core.enums import GeneralCriterion, Direction


@pytest.fixture
def alternatives():
    return ['a1', 'a2', 'a3', 'a4', 'a5']


@pytest.fixture
def criteria():
    return ['k1', 'k2']


@pytest.fixture
def alternatives_performances(alternatives, criteria):
    perf = [[10, 12],
            [12.5, 13],
            [15, 29],
            [14, 13],
            [11, 10]]
    return pd.DataFrame(data=perf, index=alternatives, columns=criteria)


@pytest.fixture
def preference_thresholds(criteria):
    preference_thresholds = [4, 0.5]
    return pd.Series(data=preference_thresholds, index=criteria)


@pytest.fixture
def indifference_thresholds(criteria):
    indifference_thresholds = [0.4, 5]
    return pd.Series(data=indifference_thresholds, index=criteria)


@pytest.fixture
def standard_deviations(criteria):
    standard_deviations = [3, 3]
    return pd.Series(data=standard_deviations, index=criteria)


@pytest.fixture
def generalized_criteria(criteria):
    generalized_criteria_list = [GeneralCriterion.U_SHAPE,
                                 GeneralCriterion.V_SHAPE]
    return pd.Series(data=generalized_criteria_list, index=criteria)


@pytest.fixture
def weights(criteria):
    weights = [1, 2]
    return pd.Series(data=weights, index=criteria)


@pytest.fixture
def directions(criteria):
    directions = [Direction.MIN, Direction.MAX]
    return pd.Series(data=directions, index=criteria)


@pytest.fixture
def vetoes(criteria):
    veto_thresholds = [3, 3]
    return pd.Series(data=veto_thresholds, index=criteria)


def test_veto_preference(alternatives, alternatives_performances, weights,
                         vetoes, directions):
    data = [[0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [1, 0, 0, 0, 1],
            [1, 0, 1, 0, 1],
            [0, 1, 1, 1, 0]]
    expected = pd.DataFrame(data=data, columns=alternatives,
                            index=alternatives)
    actual, _ = compute_veto(
        alternatives_performances=alternatives_performances, weights=weights,
        veto_thresholds=vetoes,
        directions=directions)
    assert_frame_equal(actual, expected, atol=0.006)


def test_overall_preference(alternatives, alternatives_performances, weights,
                            preference_thresholds,
                            indifference_thresholds, standard_deviations,
                            generalized_criteria, vetoes,
                            directions):
    preference, _ = compute_preference_indices(alternatives_performances,
                                               preference_thresholds,
                                               indifference_thresholds,
                                               standard_deviations,
                                               generalized_criteria,
                                               directions, weights)
    expected = pd.DataFrame(data=[[0.000, 0.333, 0.000, 0.333, 1.000],
                                  [0.667, 0.000, 0.000, 0.333, 0.667],
                                  [0.000, 0.667, 0.000, 0.667, 0.000],
                                  [0.000, 0.000, 0.000, 0.000, 0.000],
                                  [0.000, 0.000, 0.000, 0.000, 0.000]],
                            columns=alternatives, index=alternatives)
    _, _, actual = compute_veto(
        alternatives_performances=alternatives_performances, weights=weights,
        veto_thresholds=vetoes, directions=directions, preferences=preference)

    assert_frame_equal(actual, expected, atol=0.006)


if __name__ == '__main__':
    test_veto_preference(alternatives, alternatives_performances, weights,
                         vetoes, directions)
    test_overall_preference(alternatives, alternatives_performances, weights,
                            preference_thresholds,
                            indifference_thresholds, standard_deviations,
                            generalized_criteria, vetoes, directions)
