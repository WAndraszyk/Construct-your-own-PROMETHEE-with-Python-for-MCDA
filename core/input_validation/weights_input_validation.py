import pandas as pd

__all__ = ["srf_weights_validation", "surrogate_weights_validation"]

from core.aliases import NumericValue


def _check_decimal_place(decimal_place: int):
    """
    Check decimal place for weights.

    :param decimal_place: int with decimal place
    :raises TypeError: if decimal place is not valid
    """

    # Check if decimal place is integer
    if not isinstance(decimal_place, int):
        raise TypeError("Decimal place must be integer")

    # Check if decimal place is not negative
    if decimal_place < 0:
        raise ValueError("Decimal place must be positive")


def _check_criteria_weight_ratio(criteria_weight_ratio: NumericValue):
    """
    Check criteria weight ratio for SRF weights calculation.

    :param criteria_weight_ratio: integer, ratio of weights of criteria
    """

    # Check if criteria weight ratio is numeric
    if not isinstance(criteria_weight_ratio, (int, float)):
        raise TypeError("Criteria weight ratio must be numeric")

    # Check if criteria weight ratio is greater than 1
    if criteria_weight_ratio <= 1:
        raise ValueError("Criteria weight ratio must be greater than 1")


def _check_criteria_ranks(criteria_ranks: pd.Series):
    """
    Check criteria ranks for weights calculation.

    :param criteria_ranks: Series with ranks of criteria
    :raise TypeError: if criteria ranks are not valid
    """

    # Check if criteria ranks are in Series
    if not isinstance(criteria_ranks, pd.Series):
        raise TypeError("Criteria ranks must be pandas Series")

    # Check if criteria ranks are integer
    if criteria_ranks.dtype not in ['int32', 'int64']:
        raise TypeError("Criteria ranks must be integer")

    # Check if criteria ranks are greater or equal to 1
    if not all(criteria_ranks >= 1):
        raise ValueError("Criteria ranks must be greater than 1")

    # Check if criteria ranks have starts from 1
    if 1 not in criteria_ranks.values:
        raise ValueError("Criteria ranks must start from rank 1")


def srf_weights_validation(criteria_ranks: pd.Series,
                           criteria_weight_ratio: NumericValue,
                           decimal_place: int):
    """
    Check input data for SRF weights calculation.

    :param criteria_ranks: pd.Series with criteria as index and
    ranks as values
    :param criteria_weight_ratio: integer, ratio of weights of criteria
    :param decimal_place: integer, decimal place for calculations
    :raises TypeError: if any input data is not valid
    """
    _check_decimal_place(decimal_place)
    _check_criteria_weight_ratio(criteria_weight_ratio)
    _check_criteria_ranks(criteria_ranks)


def surrogate_weights_validation(criteria_ranks: pd.Series,
                                 decimal_place: int):
    """
   Check input data for surrogate weights calculation.

   :param criteria_ranks: pd.Series with criteria as index and
   criteria ranks as values
   :param decimal_place: integer, decimal place
   :raises TypeError: if any input data is not valid
   """
    _check_decimal_place(decimal_place)
    _check_criteria_ranks(criteria_ranks)
