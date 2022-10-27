import pytest
import sys
import pandas as pd
from pandas.testing import assert_frame_equal
from modular_parts.flows import calculate_promethee_outranking_flows

sys.path.append('../..')


@pytest.fixture
def alternatives_preferences():
    alternatives = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']
    return pd.DataFrame([[0, 0.06554, 0.02185, 0.07647, 0, 0.04370],
                         [0.36323, 0, 0, 0.01092, 0, 0.23526],
                         [0.5586, 0.23632, 0, 0.05462, 0.04697, 0.44973],
                         [0.92353, 0.56030, 0.36767, 0, 0.39967, 0.79555],
                         [0.52386, 0.22617, 0.03683, 0.07647, 0, 0.43958],
                         [0.12798, 0.02185, 0, 0.03277, 0, 0]], index=alternatives, columns=alternatives)


def test_promethee_outranking_flows(alternatives_preferences):
    alternatives = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']
    expected = pd.DataFrame({'positive': [0.04151, 0.12188, 0.26870, 0.60934, 0.26058, 0.03652],
                             'negative': [0.49889, 0.22204, 0.08527, 0.05025, 0.08933, 0.39276]
                             }, index=alternatives)

    actual = calculate_promethee_outranking_flows(alternatives_preferences)

    assert_frame_equal(expected, actual, atol=0.006)


if __name__ == '__main__':
    test_promethee_outranking_flows(alternatives_preferences)
