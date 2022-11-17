from pandas.testing import assert_frame_equal
from unit_tests.data.Example2Data import *
from modular_parts.preference import compute_preference_indices, compute_discordance
from modular_parts.weights import equal_weights


def test_discordance():
    weights = equal_weights(ranked_criteria=pd.Series(data=[7, 1, 3, 2, 4, 5], index=criteria))

    _, partial = compute_preference_indices(alternatives_performances, preference_thresholds,
                                            indifference_thresholds, standard_deviations,
                                            generalized_criteria,
                                            criteria_directions, weights)

    expected = pd.DataFrame(data=[[0.000, 1.000, 1.000, 1.000, 1.000, 1.000],
                                  [1.000, 0.000, 0.523, 1.000, 1.000, 1.000],
                                  [1.000, 1.000, 0.000, 1.000, 1.000, 1.000],
                                  [0.728, 1.000, 1.000, 0.000, 1.000, 1.000],
                                  [0.368, 1.000, 0.184, 1.000, 0.000, 0.553],
                                  [1.000, 1.000, 1.000, 1.000, 1.000, 0.000]], columns=alternatives, index=alternatives)

    actual, _ = compute_discordance(criteria, partial, 3)

    assert_frame_equal(actual, expected, atol=0.006)


def test_overall_preference():
    weights = equal_weights(ranked_criteria=pd.Series(data=[7, 1, 3, 2, 4, 5], index=criteria))

    preference, partial = compute_preference_indices(alternatives_performances, preference_thresholds,
                                                     indifference_thresholds, standard_deviations,
                                                     generalized_criteria,
                                                     criteria_directions, weights)

    expected = pd.DataFrame(data=[[0.000, 0.000, 0.000, 0.000, 0.000, 0.000],
                                  [0.000, 0.000, 0.186, 0.000, 0.000, 0.000],
                                  [0.000, 0.000, 0.000, 0.000, 0.000, 0.000],
                                  [0.109, 0.000, 0.000, 0.000, 0.000, 0.000],
                                  [0.281, 0.000, 0.397, 0.000, 0.000, 0.200],
                                  [0.000, 0.000, 0.000, 0.000, 0.000, 0.000]], columns=alternatives, index=alternatives)

    actual = compute_discordance(criteria, partial, 3, 3, preference)

    assert_frame_equal(actual, expected, atol=0.006)


if __name__ == '__main__':
    test_discordance()
