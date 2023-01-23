import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from core.enums import RelationType
from modular_parts.M16_PrometheeIIIRanking import calculate_promethee_iii_ranking


@pytest.fixture
def alternatives():
    return [f"a{i}" for i in range(1, 7)]


@pytest.fixture
def preferences(alternatives):
    return pd.DataFrame(
        [
            [0, 0.06554, 0.02185, 0.07647, 0, 0.04370],
            [0.36323, 0, 0, 0.01092, 0, 0.23526],
            [0.5586, 0.23632, 0, 0.05462, 0.04697, 0.44973],
            [0.92353, 0.56030, 0.36767, 0, 0.39967, 0.79555],
            [0.52386, 0.22617, 0.03683, 0.07647, 0, 0.43958],
            [0.12798, 0.02185, 0, 0.03277, 0, 0],
        ],
        index=alternatives,
        columns=alternatives,
    )


@pytest.fixture
def flows(alternatives):
    return pd.DataFrame(
        {
            "positive": [0.20756, 0.60942, 1.34350, 3.04672, 1.30291, 0.18260],
            "negative": [2.49446, 1.11018, 0.42635, 0.25125, 0.44664, 1.96382],
        },
        index=alternatives,
    )


def test_promethee_iii_ranking(flows, preferences, alternatives):
    expected_interval = pd.DataFrame(
        [
            [-3.25, -1.323],
            [-0.755, -0.247],
            [0.509, 1.326],
            [1.622, 3.969],
            [0.471, 1.241],
            [-2.537, -1.025],
        ],
        index=alternatives,
        columns=["x", "y"],
    )

    expected_pairs = [
        ("a1", "a2", RelationType.INCOMPARABLE),
        ("a1", "a3", RelationType.INCOMPARABLE),
        ("a1", "a4", RelationType.INCOMPARABLE),
        ("a1", "a5", RelationType.INCOMPARABLE),
        ("a1", "a6", RelationType.INDIFFERENCE),
        ("a2", "a1", RelationType.PREFERENCE),
        ("a2", "a3", RelationType.INCOMPARABLE),
        ("a2", "a4", RelationType.INCOMPARABLE),
        ("a2", "a5", RelationType.INCOMPARABLE),
        ("a2", "a6", RelationType.PREFERENCE),
        ("a3", "a1", RelationType.PREFERENCE),
        ("a3", "a2", RelationType.PREFERENCE),
        ("a3", "a4", RelationType.INCOMPARABLE),
        ("a3", "a5", RelationType.INDIFFERENCE),
        ("a3", "a6", RelationType.PREFERENCE),
        ("a4", "a1", RelationType.PREFERENCE),
        ("a4", "a2", RelationType.PREFERENCE),
        ("a4", "a3", RelationType.PREFERENCE),
        ("a4", "a5", RelationType.PREFERENCE),
        ("a4", "a6", RelationType.PREFERENCE),
        ("a5", "a1", RelationType.PREFERENCE),
        ("a5", "a2", RelationType.PREFERENCE),
        ("a5", "a3", RelationType.INDIFFERENCE),
        ("a5", "a4", RelationType.INCOMPARABLE),
        ("a5", "a6", RelationType.PREFERENCE),
        ("a6", "a1", RelationType.INDIFFERENCE),
        ("a6", "a2", RelationType.INCOMPARABLE),
        ("a6", "a3", RelationType.INCOMPARABLE),
        ("a6", "a4", RelationType.INCOMPARABLE),
        ("a6", "a5", RelationType.INCOMPARABLE),
    ]

    interval, pairs = calculate_promethee_iii_ranking(flows, preferences, 0.5)

    assert_frame_equal(interval, expected_interval, atol=0.006)
    assert pairs == expected_pairs
