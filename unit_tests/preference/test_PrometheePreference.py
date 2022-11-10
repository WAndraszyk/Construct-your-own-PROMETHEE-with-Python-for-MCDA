import sys
from pandas._testing import assert_frame_equal
from unit_tests.data.Example2Data import *
from modular_parts.preference import compute_preference_indices
from modular_parts.weights import equal_weights

sys.path.append('../..')


def test_preference():
    weights = equal_weights(ranked_criteria=pd.Series(data=[7, 1, 3, 2, 4, 5], index=criteria))
    expected = pd.DataFrame(data=[[0.000, 0.296, 0.250, 0.268, 0.100, 0.185],
                                  [0.462, 0.000, 0.389, 0.333, 0.296, 0.500],
                                  [0.236, 0.180, 0.000, 0.333, 0.056, 0.429],
                                  [0.399, 0.505, 0.305, 0.000, 0.223, 0.212],
                                  [0.444, 0.515, 0.487, 0.380, 0.000, 0.448],
                                  [0.286, 0.399, 0.250, 0.432, 0.133, 0.000]], columns=alternatives, index=alternatives)

    actual, _ = compute_preference_indices(alternatives_performances, preference_thresholds,
                                           indifference_thresholds, standard_deviations,
                                           generalized_criteria,
                                           criteria_directions, weights)

    assert_frame_equal(actual, expected, atol=0.006)


if __name__ == '__main__':
    test_preference()
