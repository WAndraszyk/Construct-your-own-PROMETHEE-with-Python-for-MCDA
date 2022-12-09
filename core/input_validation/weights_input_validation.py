import pandas as pd

__all__ = ["srf_weights_validation", "surrogate_weights_validation"]

from core.aliases import NumericValue


def _check_decimal_place(decimal_place: int):
    if not isinstance(decimal_place, int):
        raise TypeError("Decimal place must be integer")
    if decimal_place < 0:
        raise ValueError("Decimal place must be positive")


def _check_criteria_weight_ratio(criteria_weight_ratio: NumericValue):
    if not isinstance(criteria_weight_ratio, (int, float)):
        raise TypeError("Criteria weight ratio must be numeric")
    if criteria_weight_ratio <= 1:
        raise ValueError("Criteria weight ratio must be greater than 1")


def _check_criteria_ranks(criteria_ranks: pd.Series):
    if not isinstance(criteria_ranks, pd.Series):
        raise TypeError("Criteria ranks must be pandas Series")
    if not criteria_ranks.dtype == 'int64':
        raise TypeError("Criteria ranks must be integer")
    if not all(criteria_ranks >= 1):
        raise ValueError("Criteria ranks must be greater than 1")
    if 1 not in criteria_ranks.values:
        raise ValueError("Criteria ranks must start from rank 1")


def srf_weights_validation(criteria_ranks: pd.Series,
                           criteria_weight_ratio: NumericValue,
                           decimal_place: int):
    """
    Validate input data for SRF weights calculation.
    :param criteria_ranks: Series with ranks of criteria
    :param criteria_weight_ratio: Ratio of weights of criteria
    :param decimal_place: Decimal place for weights
    :return: None
    """
    _check_decimal_place(decimal_place)
    _check_criteria_weight_ratio(criteria_weight_ratio)
    _check_criteria_ranks(criteria_ranks)


def surrogate_weights_validation(criteria_ranks: pd.Series,
                                 decimal_place: int):
    """
   Validate input data for surrogate weights calculation.
   :param criteria_ranks: Series with ranks of criteria
   :param decimal_place: Decimal place for weights
   :return: None
   """
    _check_decimal_place(decimal_place)
    _check_criteria_ranks(criteria_ranks)
