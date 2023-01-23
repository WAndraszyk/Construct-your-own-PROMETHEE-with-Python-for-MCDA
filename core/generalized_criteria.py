import math
from typing import Union


def usual_criterion(d: Union[int, float]) -> Union[int, float]:
    """Returns 0 if difference is less or equal to 0, if not it returns 1.
    :param d: difference between two alternatives on a specified criterion

    :returns: preference value
    """
    return 1.0 if d > 0 else 0.0


def u_shape_criterion(d: Union[int, float], q: Union[int, float]) -> Union[int, float]:
    """
    Returns 0 if difference is less or equal to q, if not it returns 1.

    :param d: difference between two alternatives on a specified criterion
    :param q: threshold of indifference
    :return: preference value
    """
    if d <= q:
        return 0.0
    else:
        return 1.0


def v_shape_criterion(d: Union[int, float], p: Union[int, float]) -> Union[int, float]:
    """
    Returns 0 if difference is less or equal to p, 1 if it is greater than p.
    Else it calculates the number between 0 and 1 based on the difference.

    :param d: difference between two alternatives on a specified criterion
    :param p: threshold of strict preference
    :return: preference value
    """
    if d <= 0:
        return 0.0
    elif d <= p:
        return d / p
    else:
        return 1.0


def level_criterion(
    d: Union[int, float], p: Union[int, float], q: Union[int, float]
) -> Union[int, float]:
    """
    Returns: 0 for d<=q,
             0.5 for q<d<=p,

             1 for d>p

    :param d: difference between two alternatives on a specified criterion
    :param p: threshold of strict preference
    :param q: threshold of indifference
    :return: preference value
    """
    if d <= q:
        return 0.0
    elif d <= p:
        return 0.5
    else:
        return 1.0


def v_shape_indifference_criterion(
    d: Union[int, float], p: Union[int, float], q: Union[int, float]
) -> Union[int, float]:
    """
    Returns 0 if difference is less or equal to q, 1 if it is greater than p.
    Else it calculates the number between 0 and 1 based on the difference.

    :param d: difference between two alternatives on a specified criterion
    :param p: threshold of strict preference
    :param q: threshold of indifference
    :return: preference value
    """
    if d <= q:
        return 0.0
    elif d <= p:
        return (d - q) / (p - q)
    else:
        return 1.0


def gaussian_criterion(d: Union[int, float], s: Union[int, float]) -> Union[int, float]:
    """
    Calculates preference based on nonlinear gaussian function.

    :param s: intermediate value between q and p. Defines the inflection
              point of the preference function.
    :param d: difference between two
              alternatives on a specified criterion
    :return: preference value
    """
    e = math.e
    if d <= 0:
        return 0.0
    else:
        return 1.0 - e ** (-((d**2) / (2 * s**2)))
