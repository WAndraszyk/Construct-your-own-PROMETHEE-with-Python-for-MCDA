import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from core.enums import Direction
from modular_parts.M7_PrometheeVeto import compute_veto


@pytest.fixture
def alternatives():
    return ["a1", "a2", "a3", "a4", "a5"]


@pytest.fixture
def criteria():
    return ["k1", "k2"]


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


@pytest.fixture
def alternatives_performances(alternatives, criteria):
    perf = [[10, 12], [12.5, 13], [15, 29], [14, 13], [11, 10]]
    return pd.DataFrame(data=perf, index=alternatives, columns=criteria)


@pytest.fixture
def aggregated_preferences(alternatives):
    # alternatives vs alternatives
    aggregated_preferences = [
        [0.0, 0.333, 0.333, 0.333, 1.0],
        [0.667, 0.0, 0.333, 0.333, 0.667],
        [0.667, 0.667, 0.0, 0.667, 0.667],
        [0.667, 0.0, 0.333, 0.0, 0.667],
        [0.0, 0.333, 0.333, 0.333, 0.0],
    ]
    return pd.DataFrame(
        data=aggregated_preferences, columns=alternatives, index=alternatives
    )


def test_veto_preference(
    alternatives, alternatives_performances, weights, vetoes, directions
):
    data = [
        [0.0, 0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0, 1.0],
        [1.0, 0.0, 1.0, 0.0, 1.0],
        [0.0, 1.0, 1.0, 1.0, 0.0],
    ]
    expected = pd.DataFrame(data=data, columns=alternatives, index=alternatives)
    actual, _ = compute_veto(
        alternatives_performances=alternatives_performances,
        weights=weights,
        veto_thresholds=vetoes,
        directions=directions,
    )
    assert_frame_equal(actual, expected, atol=0.006)


def test_overall_preference(
    alternatives,
    alternatives_performances,
    weights,
    vetoes,
    directions,
    aggregated_preferences,
):
    expected = pd.DataFrame(
        data=[
            [0.000, 0.333, 0.000, 0.333, 1.000],
            [0.667, 0.000, 0.000, 0.333, 0.667],
            [0.000, 0.667, 0.000, 0.667, 0.000],
            [0.000, 0.000, 0.000, 0.000, 0.000],
            [0.000, 0.000, 0.000, 0.000, 0.000],
        ],
        columns=alternatives,
        index=alternatives,
    )
    _, _, actual = compute_veto(
        alternatives_performances=alternatives_performances,
        weights=weights,
        veto_thresholds=vetoes,
        directions=directions,
        preferences=aggregated_preferences,
    )

    assert_frame_equal(actual, expected, atol=0.006)
