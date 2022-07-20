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
