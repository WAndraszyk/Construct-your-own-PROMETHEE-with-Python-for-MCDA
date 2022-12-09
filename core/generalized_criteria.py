import math
from core.aliases import NumericValue


def usual_criterion(d: NumericValue) -> NumericValue:
    """
    Returns 0 if difference is less or equal to 0, if not it returns 1.

    :param d: difference between two alternatives on a specified criterion
    """
    return 1 if d > 0 else 0


def u_shape_criterion(d: NumericValue, q: NumericValue) -> NumericValue:
    """
    Returns 0 if difference is less or equal to q, if not it returns 1.

    :param d: difference between two alternatives on a specified criterion
    :param q: threshold of indifference
    """
    if d <= q:
        return 0
    else:
        return 1


def v_shape_criterion(d: NumericValue, p: NumericValue) -> NumericValue:
    """
    Returns 0 if difference is less or equal to p, 1 if it is greater than p.
    Else it calculates the number between 0 and 1 based on the difference.

    :param d: difference between two alternatives on a specified criterion
    :param p: threshold of strict preference
    """
    if d <= 0:
        return 0
    elif d <= p:
        return d / p
    else:
        return 1


def level_criterion(d: NumericValue, p: NumericValue, q: NumericValue
                    ) -> NumericValue:
    """
    Returns: 0 for d<=q
             0.5 for q<d<=p
             1 for d>p

    :param d: difference between two alternatives on a specified criterion
    :param p: threshold of strict preference
    :param q: threshold of indifference
    """
    if d <= q:
        return 0
    elif d <= p:
        return 0.5
    else:
        return 1


def v_shape_indifference_criterion(d: NumericValue, p: NumericValue,
                                   q: NumericValue) -> NumericValue:
    """
    Returns 0 if difference is less or equal to q, 1 if it is greater than p.
    Else it calculates the number between 0 and 1 based on the difference.

    :param d: difference between two alternatives on a specified criterion
    :param p: threshold of strict preference
    :param q: threshold of indifference
    """
    if d <= q:
        return 0
    elif d <= p:
        return (d - q) / (p - q)
    else:
        return 1


def gaussian_criterion(d: NumericValue, s: NumericValue) -> NumericValue:
    """
    Calculates preference based on nonlinear gaussian function.

    :param s: intermediate value between q and p. Defines the inflection
    point of the preference function.
    :param d: difference between two
    alternatives on a specified criterion
    """
    e = math.e
    if d <= 0:
        return 0
    else:
        return 1 - e ** (-((d ** 2) / (2 * s ** 2)))
