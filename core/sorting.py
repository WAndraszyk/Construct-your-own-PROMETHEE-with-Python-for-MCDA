"""
.. deprecated:: 0.3.4
    The whole module is deprecated. Class :class:`RelationType` and type alias
    `Relation` should be imported from :mod:`mcda.core.relations` instead.
"""
from typing import List

from deprecated.sphinx import deprecated

import mcda.core.relations as relations

from .aliases import NumericValue

Relation = relations.Relation

RelationType = relations.RelationType


@deprecated(
    reason="Since pandas package is used, its basic functions should be used "
    "instead. In this case: :meth:`pandas.Series.sort_values`",
    version="0.3.4",
)
def rank_values(
    values: List[NumericValue], reverse: bool = False
) -> List[int]:
    """Rank values.

    First value in ranking order has the smallest rank.
    By default, it ranks how big values are (i.e value with rank ``0`` is
    the biggest value).
    To reverse ranking order, put parameter `reverse` to ``True``.

    :param values:
    :param reverse:
    :return: ranks list
    """
    order = sorted(
        range(len(values)), key=lambda i: values[i], reverse=not reverse
    )
    return [order.index(i) for i, _ in enumerate(values)]


@deprecated(
    reason="Since pandas package is used, its basic functions should be used "
    "instead. In this case: :meth:`pandas.Series.sort_values`",
    version="0.3.4",
)
def sort_elements_by_values(
    values: List[NumericValue], *elements: List, reverse: bool = False
):
    """Sort elements by their values.

    By default, elements are sorted by decreasing values.
    To reverse ranking order, put parameter `reverse` to ``True``.

    :param elements: different lists of any elements that must be sorted
    :param values:
    :param reverse:

    .. warning:: input elements are sorted directly and are therefore modified
    """
    ranks = rank_values(values, reverse)
    for i in range(len(elements)):
        for j, v in enumerate([a for _, a in sorted(zip(ranks, elements[i]))]):
            elements[i][j] = v
