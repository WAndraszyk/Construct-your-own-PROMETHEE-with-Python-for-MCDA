import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from modular_parts.preference import compute_reinforced_preference
from core.enums import GeneralCriterion, Direction


@pytest.fixture
def alternatives():
    return ['a1', 'a2', 'a3']


@pytest.fixture
def profiles():
    return ['b1', 'b2']


@pytest.fixture
def criteria():
    return ['k1', 'k2']


@pytest.fixture
def alternatives_performances(alternatives, criteria):
    perf = [[5, 5],
            [1, 1],
            [4, 4]]
    return pd.DataFrame(data=perf, index=alternatives, columns=criteria)


@pytest.fixture
def profiles_performances(profiles, criteria):
    profiles_performances = [[1, 1],
                             [4, 4]]
    return pd.DataFrame(data=profiles_performances, index=profiles,
                        columns=criteria)


@pytest.fixture
def preference_thresholds(criteria):
    preference_thresholds = [2, 2]
    return pd.Series(data=preference_thresholds, index=criteria)


@pytest.fixture
def indifference_thresholds(criteria):
    indifference_thresholds = [None, None]
    return pd.Series(data=indifference_thresholds, index=criteria)


@pytest.fixture
def reinforcement_thresholds(criteria):
    reinforcement_thresholds = [3, 3]
    return pd.Series(data=reinforcement_thresholds, index=criteria)


@pytest.fixture
def reinforcement_factors(criteria):
    reinforcement_factors = [5, 5]
    return pd.Series(data=reinforcement_factors, index=criteria)


@pytest.fixture
def generalized_criteria(criteria):
    generalized_criteria_list = [GeneralCriterion.V_SHAPE,
                                 GeneralCriterion.V_SHAPE]
    return pd.Series(data=generalized_criteria_list, index=criteria)


@pytest.fixture
def weights(criteria):
    weights = [1, 2]
    return pd.Series(data=weights, index=criteria)


@pytest.fixture
def directions(criteria):
    directions = [Direction.MAX, Direction.MIN]
    return pd.Series(data=directions, index=criteria)


@pytest.fixture
def s_parameters(criteria):
    s_parameters = [None, None]
    return pd.Series(data=s_parameters, index=criteria)


def test_reinforced_preference(alternatives, alternatives_performances,
                               preference_thresholds, indifference_thresholds,
                               s_parameters,
                               generalized_criteria, directions,
                               reinforcement_thresholds,
                               reinforcement_factors,
                               weights, profiles_performances, profiles):
    data1 = [[0.714, 0.167], [0, 0.667], [0.333, 0]]
    expected1 = pd.DataFrame(data=data1, columns=profiles, index=alternatives)
    data2 = [[0.909, 0, 0.667], [0.333, 0.333, 0]]
    expected2 = pd.DataFrame(data=data2, columns=alternatives, index=profiles)

    actual, _ = compute_reinforced_preference(alternatives_performances,
                                              preference_thresholds,
                                              indifference_thresholds,
                                              s_parameters,
                                              generalized_criteria,
                                              directions,
                                              reinforcement_thresholds,
                                              reinforcement_factors, weights,
                                              profiles_performances)

    assert_frame_equal(actual[0], expected1, atol=0.006)
    assert_frame_equal(actual[1], expected2, atol=0.006)


if __name__ == '__main__':
    test_reinforced_preference(alternatives, alternatives_performances,
                               preference_thresholds, indifference_thresholds,
                               s_parameters,
                               generalized_criteria, directions,
                               reinforcement_thresholds,
                               reinforcement_factors,
                               weights, profiles_performances, profiles)
