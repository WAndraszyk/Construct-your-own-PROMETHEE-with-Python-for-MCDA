import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from core.enums import CompareProfiles, Direction
from modular_parts.M20_FlowSortI import calculate_flowsortI_sorted_alternatives


@pytest.fixture
def categories():
    return [f"C{i}" for i in range(1, 5)]


@pytest.fixture
def category_profiles_performances():
    profiles = [f"r{i}" for i in range(1, 6)]
    criteria = [f"g{i}" for i in range(1, 6)]
    return pd.DataFrame(
        [
            [0, 0, 0, 0, 0],
            [25, 25, 25, 25, 25],
            [50, 50, 50, 50, 50],
            [75, 75, 75, 75, 75],
            [100, 100, 100, 100, 100],
        ],
        index=profiles,
        columns=criteria,
    )


@pytest.fixture
def criteria_directions():
    criteria = [f"g{i}" for i in range(1, 6)]
    return pd.Series(
        [
            Direction.MAX,
            Direction.MAX,
            Direction.MAX,
            Direction.MAX,
            Direction.MAX,
        ],
        index=criteria,
    )


@pytest.fixture
def alternatives_flows():
    alternatives = [f"a{i}" for i in range(1, 4)]
    return pd.DataFrame(
        {"positive": [0.48, 0.20, 0.40], "negative": [0.52, 0.80, 0.40]},
        index=alternatives,
    )


@pytest.fixture
def category_profiles_flows():
    profiles = [f"r{i}" for i in range(1, 6)]
    return pd.DataFrame(
        {
            "positive": [0.0, 0.4, 0.6, 0.866667, 1.0],
            "negative": [1.0, 0.466667, 0.333333, 0.0, 0.0],
        },
        index=profiles,
    )


@pytest.fixture
def comparison_with_profiles():
    return CompareProfiles.LIMITING_PROFILES


def test(
    categories,
    category_profiles_performances,
    criteria_directions,
    alternatives_flows,
    category_profiles_flows,
    comparison_with_profiles,
):
    actual_classification = calculate_flowsortI_sorted_alternatives(
        categories,
        category_profiles_performances,
        criteria_directions,
        alternatives_flows,
        category_profiles_flows,
        comparison_with_profiles,
    )

    expected_classification = pd.DataFrame(
        {"worse": ["C1", "C1", "C1"], "better": ["C2", "C1", "C2"]},
        index=alternatives_flows.index,
    )
    assert_frame_equal(expected_classification, actual_classification)
