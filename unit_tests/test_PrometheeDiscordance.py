import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from modular_parts.M6_PrometheeDiscordance import compute_discordance


@pytest.fixture
def criteria():
    return ["g1", "g2", "g3", "g4", "g5", "g6"]


@pytest.fixture
def alternatives():
    return ["a1", "a2", "a3", "a4", "a5", "a6"]


@pytest.fixture
def aggregated_preferences(alternatives):
    # alternatives vs alternatives
    preferences = [
        [0.0, 0.296, 0.25, 0.269, 0.1, 0.185],
        [0.463, 0.0, 0.389, 0.333, 0.296, 0.5],
        [0.235, 0.18, 0.0, 0.333, 0.056, 0.429],
        [0.399, 0.506, 0.305, 0.0, 0.224, 0.212],
        [0.444, 0.515, 0.487, 0.38, 0.0, 0.448],
        [0.287, 0.399, 0.25, 0.431, 0.133, 0.0],
    ]
    return pd.DataFrame(data=preferences, index=alternatives, columns=alternatives)


@pytest.fixture
def partial_preferences(alternatives, criteria):
    # alternatives vs alternatives
    partial_preferences = [
        [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        [1.0, 0.0, 1.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        [1.0, 1.0, 1.0, 0.0, 1.0, 1.0],
        [1.0, 1.0, 1.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 1.0, 0.333333, 0.6, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.066667, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.733333, 0.666667, 0.0, 0.266667, 0.0],
        [0.0, 0.466667, 0.4, 0.0, 0.0, 0.0],
        [0.2, 1.0, 1.0, 0.533333, 0.8, 0.0],
        [0.0, 0.0, 0.0, 0.777778, 0.0, 0.111111],
        [0.777778, 0.0, 0.333333, 1.0, 0.777778, 1.0],
        [0.333333, 0.0, 0.0, 1.0, 0.333333, 0.555556],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.777778, 0.0, 0.111111],
        [0.0, 0.0, 0.0, 0.555556, 0.0, 0.0],
        [0.0, 0.5, 0.5, 0.5, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.5, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.5, 0.0, 0.0, 0.0, 0.0],
        [0.5, 1.0, 0.5, 0.5, 0.0, 0.5],
        [0.5, 1.0, 0.5, 0.5, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 1.0, 1.0, 1.0, 1.0],
        [1.0, 0.0, 0.0, 1.0, 0.0, 1.0],
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 1.0, 1.0, 0.0, 1.0],
        [1.0, 0.0, 0.0, 1.0, 0.0, 0.0],
        [0.0, 0.273851, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.076884, 0.513248, 0.0, 0.0, 0.0, 0.019801],
        [0.393469, 0.802101, 0.16473, 0.0, 0.076884, 0.273851],
        [0.16473, 0.624689, 0.019801, 0.0, 0.0, 0.076884],
        [0.019801, 0.393469, 0.0, 0.0, 0.0, 0.0],
    ]
    pp_index = pd.MultiIndex.from_product([criteria, alternatives])
    return pd.DataFrame(data=partial_preferences, index=pp_index, columns=alternatives)


def test_discordance(criteria, alternatives, partial_preferences):
    expected = pd.DataFrame(
        data=[
            [0.000, 1.000, 1.000, 1.000, 1.000, 1.000],
            [1.000, 0.000, 0.523, 1.000, 1.000, 1.000],
            [1.000, 1.000, 0.000, 1.000, 1.000, 1.000],
            [0.728, 1.000, 1.000, 0.000, 1.000, 1.000],
            [0.368, 1.000, 0.184, 1.000, 0.000, 0.553],
            [1.000, 1.000, 1.000, 1.000, 1.000, 0.000],
        ],
        columns=alternatives,
        index=alternatives,
    )

    actual, _ = compute_discordance(criteria, partial_preferences, 3)

    assert_frame_equal(actual, expected, atol=0.006)


def test_overall_preference(
    criteria, alternatives, aggregated_preferences, partial_preferences
):
    expected_discordance = pd.DataFrame(
        data=[
            [0.000, 1.000, 1.000, 1.000, 1.000, 1.000],
            [1.000, 0.000, 0.523, 1.000, 1.000, 1.000],
            [1.000, 1.000, 0.000, 1.000, 1.000, 1.000],
            [0.728, 1.000, 1.000, 0.000, 1.000, 1.000],
            [0.368, 1.000, 0.184, 1.000, 0.000, 0.553],
            [1.000, 1.000, 1.000, 1.000, 1.000, 0.000],
        ],
        columns=alternatives,
        index=alternatives,
    )

    expected = pd.DataFrame(
        data=[
            [0.000, 0.000, 0.000, 0.000, 0.000, 0.000],
            [0.000, 0.000, 0.186, 0.000, 0.000, 0.000],
            [0.000, 0.000, 0.000, 0.000, 0.000, 0.000],
            [0.109, 0.000, 0.000, 0.000, 0.000, 0.000],
            [0.281, 0.000, 0.397, 0.000, 0.000, 0.200],
            [0.000, 0.000, 0.000, 0.000, 0.000, 0.000],
        ],
        columns=alternatives,
        index=alternatives,
    )

    actual_discordance, _, actual = compute_discordance(
        criteria, partial_preferences, 3, 3, aggregated_preferences
    )

    assert_frame_equal(actual, expected, atol=0.006)
    assert_frame_equal(actual_discordance, expected_discordance, atol=0.006)
