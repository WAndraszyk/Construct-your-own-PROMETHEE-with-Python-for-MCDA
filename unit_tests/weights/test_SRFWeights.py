import pytest
import sys
import pandas as pd
from pandas.testing import assert_series_equal
from modular_parts.weights import calculate_srf_weights

sys.path.append('../..')


@pytest.fixture
def criteria_ranks():
    return pd.Series({
        'a': 6, 'b': 4, 'c': 1,
        'd': 2, 'e': 5, 'f': 4,
        'g': 1, 'h': 6, 'i': 4,
        'j': 4, 'k': 7, 'l': 1,
    })


@pytest.fixture
def criteria_weight_ratio():
    return 6.5


@pytest.fixture
def decimal_place():
    return 1


def test_srf_weights(criteria_ranks, criteria_weight_ratio, decimal_place):
    expected = pd.Series({
        'a': 13.2, 'b': 8.9, 'c': 2.4,
        'd': 4.5, 'e': 11.0, 'f': 8.9,
        'g': 2.4, 'h': 13.2, 'i': 8.9,
        'j': 8.9, 'k': 15.3, 'l': 2.4,
    })

    actual = calculate_srf_weights(criteria_ranks, criteria_weight_ratio, decimal_place)

    assert_series_equal(expected, actual, atol=0.006)


if __name__ == '__main__':
    test_srf_weights(criteria_ranks, criteria_weight_ratio, decimal_place)
