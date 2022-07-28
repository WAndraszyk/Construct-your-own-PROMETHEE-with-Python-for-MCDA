from typing import List

from core.aliases import NumericValue


def directed_alternatives_performances(alternatives_performances: List[List[NumericValue]],
                                       directions: List[NumericValue]) -> List[List[NumericValue]]:
    """
    Changes value of alternative performance to the opposite value if the direction of preference is
    min (represented by 0)

    :param alternatives_performances: 2D list of alternatives' value at every criterion
    :param directions: directions of preference of criteria
    :return: 2D list of alternatives' value at every criterion
    """
    for i in range(len(directions)):
        if directions[i] == 0:
            for j in range(len(alternatives_performances)):
                alternatives_performances[j][i] = -alternatives_performances[j][i]

    return alternatives_performances


def deviations(criteria, alternatives_performances) -> List[List[List[NumericValue]]]:
    """
    Compares alternatives on criteria.

    :return: 3D matrix of deviations in evaluations on criteria
    """
    deviations_list = []
    for k in range(len(criteria)):
        comparisons = []
        for i in range(len(alternatives_performances)):
            comparison_direct = []
            for j in range(len(alternatives_performances)):
                comparison_direct.append(
                    alternatives_performances[i][k] - alternatives_performances[j][k])
            comparisons.append(comparison_direct)
        deviations_list.append(comparisons)
    return deviations_list
