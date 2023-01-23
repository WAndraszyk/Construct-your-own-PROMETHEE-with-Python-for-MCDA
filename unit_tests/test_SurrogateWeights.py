import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from core.enums import SurrogateMethod
from modular_parts.M1_SurrogateWeights import surrogate_weights


@pytest.fixture
def criteria_ranks():
    return pd.Series(
        {
            "a": 6,
            "b": 4,
            "c": 1,
            "d": 2,
            "e": 5,
            "f": 4,
            "g": 1,
            "h": 6,
            "i": 4,
            "j": 4,
            "k": 7,
            "l": 1,
        }
    )


@pytest.fixture
def decimal_place():
    return 3


def test_equal_weights(criteria_ranks, decimal_place):
    expected = pd.Series(
        {
            "a": 0.083,
            "b": 0.083,
            "c": 0.083,
            "d": 0.083,
            "e": 0.083,
            "f": 0.083,
            "g": 0.083,
            "h": 0.083,
            "i": 0.083,
            "j": 0.083,
            "k": 0.083,
            "l": 0.083,
        },
        name="weights",
    )
    actual = surrogate_weights(criteria_ranks, SurrogateMethod.EW, decimal_place)
    assert_series_equal(expected, actual, atol=0.006)


def test_rank_sum(criteria_ranks, decimal_place):
    expected = pd.Series(
        {
            "a": 0.09,
            "b": 0.115,
            "c": 0.154,
            "d": 0.141,
            "e": 0.103,
            "f": 0.115,
            "g": 0.154,
            "h": 0.09,
            "i": 0.115,
            "j": 0.115,
            "k": 0.077,
            "l": 0.154,
        },
        name="weights",
    )
    actual = surrogate_weights(criteria_ranks, SurrogateMethod.RS, decimal_place)
    assert_series_equal(expected, actual, atol=0.006)


def test_reciprocal_of_ranks(criteria_ranks, decimal_place):
    expected = pd.Series(
        {
            "a": 0.054,
            "b": 0.081,
            "c": 0.322,
            "d": 0.161,
            "e": 0.064,
            "f": 0.081,
            "g": 0.322,
            "h": 0.054,
            "i": 0.081,
            "j": 0.081,
            "k": 0.046,
            "l": 0.322,
        },
        name="weights",
    )
    actual = surrogate_weights(criteria_ranks, SurrogateMethod.RR, decimal_place)
    assert_series_equal(expected, actual, atol=0.006)


def test_rank_order_centroid(criteria_ranks, decimal_place):
    expected = pd.Series(
        {
            "a": 0.068,
            "b": 0.106,
            "c": 0.259,
            "d": 0.175,
            "e": 0.085,
            "f": 0.106,
            "g": 0.259,
            "h": 0.068,
            "i": 0.106,
            "j": 0.106,
            "k": 0.054,
            "l": 0.259,
        },
        name="weights",
    )
    actual = surrogate_weights(criteria_ranks, SurrogateMethod.ROC, decimal_place)
    assert_series_equal(expected, actual, atol=0.006)
