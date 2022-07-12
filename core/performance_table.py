"""This module gathers all functions concerning manipulation of performance
tables.

"""

__all__ = [
    "apply_criteria_functions",
    "apply_criteria_weights",
    "get_alternative_values",
    "get_alternative_values_at",
    "get_criterion_values",
    "get_criterion_values_at",
    "is_numeric",
    "is_within_criteria_scales",
    "normalize",
    "sum_table",
    "transform",
    "within_criteria_scales",
]

from typing import Dict, Union, cast

from pandas import Series
from pandas.api.types import is_numeric_dtype  # type: ignore

from .aliases import Function, NumericValue, PerformanceTable
from .scales import Scale


def is_numeric(performance_table: PerformanceTable) -> bool:
    """Check whether performance table is numeric.

    :param performance_table:
    :return:
    :rtype: bool
    """
    for col in performance_table.columns:
        if not is_numeric_dtype(performance_table[col]):
            return False
    return True


def apply_criteria_functions(
    performance_table: PerformanceTable, functions: Dict[str, Function]
) -> PerformanceTable:
    """Apply criteria functions to performance table and return result.

    :param performance_table:
    :param functions: functions identified by their criterion
    :return:
    """
    return cast(
        PerformanceTable,
        performance_table.apply(lambda col: col.apply(functions[col.name])),
    )


def apply_criteria_weights(
    performance_table: PerformanceTable,
    criteria_weights: Dict[str, NumericValue],
) -> PerformanceTable:
    """Apply criteria weights to a performance table and return result.

    :param performance_table:
    :param criteria_weights: weights identified by their criterion
    :return:
    """
    return cast(
        PerformanceTable,
        performance_table.apply(lambda col: criteria_weights[col.name] * col),
    )


def transform(
    performance_table: PerformanceTable,
    in_scales: Dict[str, Scale],
    out_scales: Dict[str, Scale],
) -> PerformanceTable:
    """Transform performances table between scales.

    :param performance_table:
    :param in_scales: current criteria scales
    :param out_scales: target criteria scales
    :return: transformed performance table
    """
    functions = {
        criterion: (
            cast(
                Function,
                lambda x, c=criterion: in_scales[c].transform_to(
                    x, out_scales[c]
                ),
            )
        )  # https://bugs.python.org/issue13652
        for criterion in in_scales.keys()
    }
    return apply_criteria_functions(performance_table, functions)


def get_alternative_values(
    performance_table: PerformanceTable, alternative: str
) -> Series:
    """Get performances associated to an alternative.

    :param performance_table:
    :param alternative: alternative label
    :return:
    """
    return performance_table.loc[alternative]


def get_criterion_values(
    performance_table: PerformanceTable, criterion: str
) -> Series:
    """Get performances associated to a criterion.

    :param performance_table:
    :param criterion: criterion label
    :return:
    """
    return performance_table[criterion]


def get_alternative_values_at(
    performance_table: PerformanceTable, index: int
) -> Series:
    """Get performances associated to an alternative index.

    :param performance_table:
    :param index: alternative index
    :return:
    """
    return performance_table.iloc[index]


def get_criterion_values_at(
    performance_table: PerformanceTable, index: int
) -> Series:
    """Get performances associated to a criterion index.

    :param performance_table:
    :param index: criterion index
    :return:
    """
    return performance_table.iloc[:, index]


def normalize_without_scales(
    performance_table: PerformanceTable, axis: int = 0
) -> PerformanceTable:
    """Normalize performance table along given axis (min-max normalization).

    `axis` parameter changes what is returned:

    * ``0``: normalization is done per criterion
    * ``1``: normalization is done per alternative

    :param performance_table:
    :param axis:
    :return:
    :raise TypeError: if performance table is not numeric
    """
    return cast(
        PerformanceTable,
        performance_table.apply(
            lambda x: (x - x.min()) / (x.max() - x.min()),
            axis=axis,  # type: ignore
        ),
    )


def normalize(
    performance_table: PerformanceTable, scales: Dict[str, Scale] = None
) -> PerformanceTable:
    """Normalize performance table using criteria scales.

    :param performance_table:
    :param scales:
    :return:
    """
    if scales is None:
        return normalize_without_scales(performance_table)
    # return transform(
    #    performance_table,
    #    scales,
    #    {criterion: get_normalized_scale() for criterion in scales.keys()},
    # )
    return apply_criteria_functions(
        performance_table,
        {
            criterion: cast(
                Function, lambda x, c=criterion: scales[c].normalize(x)
            )
            for criterion in scales.keys()
        },
    )


def within_criteria_scales(
    performance_table: PerformanceTable, scales: Dict[str, Scale]
) -> PerformanceTable:
    """Return a table indicating which performances are within their respective
    criterion scale.

    :param performance_table:
    :param scales:
    :return:
    """
    return apply_criteria_functions(
        performance_table,
        {
            criterion: cast(Function, lambda x, c=criterion: x in scales[c])
            for criterion in scales.keys()
        },
    )


def is_within_criteria_scales(
    performance_table: PerformanceTable, scales: Dict[str, Scale]
) -> bool:
    """Check whether all cells are within their respective criteria scales.

    :param performance_table:
    :param scales:
    :return:
    """
    return within_criteria_scales(performance_table, scales).all(None)


def sum_table(
    performance_table: PerformanceTable, axis: int = None
) -> Union[Series, NumericValue]:
    """Sum performances.

    Behaviour depends on `axis` value:

    * ``0``: returns column sums as a list
    * ``1``: returns row sums as a list
    * else: returns sum on both dimension as a numeric value

    :param performance_table:
    :param axis: axis on which the sum is made
    :return:

    .. note:: Non-numeric values are simply ignored as well as non-numeric sums
    """
    if axis is not None:
        return performance_table.sum(axis=axis, numeric_only=True)
    return performance_table.sum(numeric_only=True).sum()
