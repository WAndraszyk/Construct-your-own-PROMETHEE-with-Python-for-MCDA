import pytest
import pandas as pd
from pandas._testing import assert_frame_equal
from modular_parts.ranking import calculate_promethee_iii_ranking


@pytest.fixture
def alternatives():
    return ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']


@pytest.fixture
def preferences(alternatives):
    return pd.DataFrame([[0, 0.06554, 0.02185, 0.07647, 0, 0.04370],
                         [0.36323, 0, 0, 0.01092, 0, 0.23526],
                         [0.5586, 0.23632, 0, 0.05462, 0.04697, 0.44973],
                         [0.92353, 0.56030, 0.36767, 0, 0.39967, 0.79555],
                         [0.52386, 0.22617, 0.03683, 0.07647, 0, 0.43958],
                         [0.12798, 0.02185, 0, 0.03277, 0, 0]], index=alternatives, columns=alternatives)


@pytest.fixture
def flows(alternatives):
    return pd.DataFrame({'positive': [0.20756, 0.60942, 1.34350, 3.04672, 1.30291, 0.18260],
                         'negative': [2.49446, 1.11018, 0.42635, 0.25125, 0.44664, 1.96382]
                         }, index=alternatives)


def test_promethee_iii_ranking(flows, preferences, alternatives):
    expected_interval = pd.DataFrame([[-3.25, -1.323],
                                      [-0.755, -0.247],
                                      [0.509, 1.326],
                                      [1.622, 3.969],
                                      [0.471, 1.241],
                                      [-2.537, -1.025]], index=alternatives, columns=["x", "y"])
    expected_pairs = pd.DataFrame([['I', '?', '?', '?', '?', 'I'],
                                   ['P', 'I', '?', '?', '?', 'P'],
                                   ['P', 'P', 'I', '?', 'I', 'P'],
                                   ['P', 'P', 'P', 'I', 'P', 'P'],
                                   ['P', 'P', 'I', '?', 'I', 'P'],
                                   ['I', '?', '?', '?', '?', 'I']], index=alternatives, columns=alternatives)

    interval, pairs = calculate_promethee_iii_ranking(flows, preferences, 0.5)

    assert_frame_equal(interval, expected_interval, atol=0.006)
    assert_frame_equal(pairs, expected_pairs, atol=0.006)


if __name__ == '__main__':
    test_promethee_iii_ranking(flows, preferences, alternatives)
