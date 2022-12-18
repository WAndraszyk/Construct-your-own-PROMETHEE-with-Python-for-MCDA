import pandas as pd

from core.enums import GeneralCriterion, Direction

__all__ = ["intervalp2clust_validation", "ordered_clustering_validation",
           "promethee_II_ordered_clustering_validation",
           "promethee_cluster_validation"]


def _check_alternatives_performances(alternatives_performances: pd.DataFrame):
    """
    Check if alternatives performances are valid.

    :param alternatives_performances: pd.DataFrame with alternatives as index
    and criteria as columns
    :raise ValueError: if alternatives performances are not valid
    """

    # Check if alternatives performances are a DataFrame
    if not isinstance(alternatives_performances, pd.DataFrame):
        raise ValueError("Alternatives performances should be passed "
                         "as a DataFrame")

    # Check if alternatives performances are numeric
    if not alternatives_performances.dtypes.values.all() in ['int32',
                                                             'int64',
                                                             'float32',
                                                             'float64']:
        raise ValueError("Alternatives performances should be passed "
                         "with int or float values")


def _check_if_criteria_are_the_same(criteria_1: pd.Index,
                                    criteria_2: pd.Index):
    """
    Check if two criteria are the same.

    :param criteria_1: pd.Index with criteria names
    :param criteria_2: pd.Index with criteria names
    :raises ValueError: if criteria are not the same
    """

    # Check if criteria are the same
    if not criteria_1.equals(criteria_2):
        raise ValueError("Criteria are not the same in different objects")


def _check_preference_thresholds(preference_thresholds: pd.Series,
                                 criteria: pd.Index):
    """
    Check if preference thresholds are valid.

    :param preference_thresholds: pd.Series with criteria as index and
    preference thresholds as values
    :param criteria: pd.Index with criteria names
    :raise ValueError: if preference thresholds are not valid
    """

    # Check if preference thresholds are a Series
    if not isinstance(preference_thresholds, pd.Series):
        raise TypeError("Preference thresholds should be passed as "
                        "a Series object")

    _check_if_criteria_are_the_same(preference_thresholds.index, criteria)

    # Check if preference thresholds are numeric
    for threshold in preference_thresholds:
        if not (isinstance(threshold, int) or isinstance(threshold, float)
                or threshold is None):
            raise TypeError("Preference thresholds should be numeric values"
                            " or None")

    # Check if preference thresholds are not negative
    if (preference_thresholds < 0).any():
        raise ValueError("Preference thresholds can not be lower than 0")


def _check_indifference_thresholds(indifference_thresholds: pd.Series,
                                   criteria: pd.Index):
    """
    Check if indifference thresholds are valid.

    :param indifference_thresholds: pd.Series with criteria as index and
    indifference thresholds as values
    :param criteria: pd.Index with criteria names
    :raise ValueError: if indifference thresholds are not valid
    """

    # Check if indifference thresholds are a Series
    if not isinstance(indifference_thresholds, pd.Series):
        raise TypeError("Indifference thresholds should be passed as a "
                        "Series object")

    _check_if_criteria_are_the_same(indifference_thresholds.index, criteria)

    # Check if indifference thresholds are numeric or None
    for threshold in indifference_thresholds:
        if not (isinstance(threshold, int) or isinstance(threshold, float)
                or threshold is None):
            raise TypeError("Indifference thresholds should be numeric values"
                            " or None")

    # Check if indifference thresholds are not negative
    if (indifference_thresholds < 0).any():
        raise ValueError("Indifference thresholds can not be lower than 0")


def _check_standard_deviations(standard_deviations: pd.Series,
                               criteria: pd.Index):
    """
    Check if standard deviations are valid.

    :param standard_deviations: pd.Series with criteria as index and
    standard deviations as values
    :param criteria: pd.Index with criteria names
    :raise ValueError: if standard deviations are not valid
    """

    # Check if standard deviations are a Series
    if not isinstance(standard_deviations, pd.Series):
        raise TypeError("Standard deviations should be passed as a "
                        "Series object")

    _check_if_criteria_are_the_same(standard_deviations.index, criteria)

    # Check if standard deviations thresholds are numeric
    for deviation in standard_deviations:
        if not (isinstance(deviation, int) or isinstance(deviation, float)
                or deviation is None):
            raise TypeError("Standard deviations should be numeric values"
                            " or None")

    # Check if standard deviations are not negative
    if (standard_deviations < 0).any():
        raise ValueError("Standard deviations can not be lower than 0")


def _check_generalized_criteria(generalized_criteria: pd.Series):
    """
    Check if generalized criteria are valid.

    :param generalized_criteria: pd.Series with criteria as index and
    Generalized Criterion objects as values
    :raise ValueError: if any Generalized criterion is not valid
    """

    # Check if generalized criteria are a Series
    if not isinstance(generalized_criteria, pd.Series):
        raise ValueError("Generalized criteria should be passed as a Series")

    if not all((isinstance(criterion, GeneralCriterion) for
                criterion in generalized_criteria)):
        raise ValueError("Generalized criteria should be "
                         "core.enums.PreferenceFunction enums")


def _check_criteria_directions(criteria_directions: pd.Series):
    """
    Check if criteria directions are valid.

    :param criteria_directions: pd.Series with criteria as index and
    Direction objects as values
    :raise ValueError: if any criteria direction is not valid
    """

    # Check if criteria directions are a Series
    if not isinstance(criteria_directions, pd.Series):
        raise ValueError("Criteria directions should be a Series object")

    # Check if criteria directions are Direction enums
    if criteria_directions.values.any() not in [Direction.MAX, Direction.MIN]:
        raise ValueError(
            "Criteria directions should be core.enums.Direction enums")


def _check_weights(weights: pd.Series):
    """
    Check if weights are valid.

    :param weights: pd.Series with criteria as index a weights as values
    :raises ValueError: if weights are not valid
    """

    # Check if weights are a Series
    if not isinstance(weights, pd.Series):
        raise ValueError("Criteria weights should be passed as a"
                         " Series object")

    # Check if weights are numeric
    if weights.dtype not in ['int32', 'int64', 'float32', 'float64']:
        raise ValueError("Weights should be a numeric values")

    # Check if all weights are positive
    if (weights <= 0).any():
        raise ValueError("Weights should be positive")


def _check_preference_thresholds_better_than_indifference_thresholds(
        preference_thresholds: pd.Series,
        indifference_thresholds: pd.Series):
    """
    Check if preference thresholds are better than indifference thresholds.

    :param preference_thresholds: pd.Series with criteria as index and
    preference thresholds as values
    :param indifference_thresholds: pd.Series with criteria as index and
    indifference thresholds as values
    :raise ValueError: if any preference threshold is not better
    than indifference threshold
    """

    # Check if preference thresholds are better than indifference thresholds
    if (preference_thresholds[
            preference_thresholds < indifference_thresholds] != 0).any():
        raise ValueError(
            "Preference thresholds should be greater than "
            "indifference thresholds")


def _check_if_all_inputs_have_the_same_criteria(
        alternatives_performances: pd.DataFrame,
        preference_thresholds: pd.Series,
        indifference_thresholds: pd.Series,
        standard_deviations: pd.Series,
        generalized_criteria: pd.Series,
        criteria_directions: pd.Series,
        criteria_weights: pd.Series):
    """
    Check if all inputs have the same criteria.

    :param alternatives_performances: pd.DataFrame with alternatives as index
    and criteria as columns
    :param preference_thresholds: pd.Series with criteria as index and
    preference thresholds as values
    :param indifference_thresholds: pd.Series with criteria as index and
    indifference thresholds as values
    :param standard_deviations: pd.Series with criteria as index and
    standard deviations as values
    :param generalized_criteria: pd.Series with criteria as index and
    Generalized Criterion objects as values
    :param criteria_directions: pd.Series with criteria as index and
    Direction objects as values
    :param criteria_weights: pd.Series with criteria as index and
    weights as values
    :raise ValueError: if any input has different criteria
    """

    # Check if all inputs have the same criteria
    if not (
            alternatives_performances.columns.all() ==
            preference_thresholds.index.all() ==
            preference_thresholds.index.all() ==
            indifference_thresholds.index.all() ==
            standard_deviations.index.all() ==
            generalized_criteria.index.all() ==
            criteria_directions.index.all() == criteria_weights.index.all()):
        raise ValueError("All objects should have the same criteria")


def _check_n_clusters(alternatives_performances: pd.DataFrame,
                      n_clusters: int):
    """
    Check if number of categories is valid.

    :param alternatives_performances: pd.DataFrame with alternatives as index
    and criteria as columns
    :param n_clusters: number of categories
    :raise ValueError: if number of categories is not valid
    """

    # Check if number of categories is greater than number of alternatives
    if alternatives_performances.shape[0] <= n_clusters:
        raise ValueError(
            "Number of categories should be lower than number "
            "of alternatives")

    # Check if number of categories is greater than 1
    if n_clusters < 2:
        raise ValueError("Number of categories should be greater than 1")


def _check_max_iterations(number_of_iterations: int):
    """
    Check if number of max iterations is valid.

    :param number_of_iterations: number of max iterations
    :raise ValueError: if number of max iterations is not valid
    """

    # Check if number of max iterations is integer
    if not isinstance(number_of_iterations, int):
        raise ValueError("Max iterations should be passed as an integer")

    # Check if number of max iterations is greater than 0
    if number_of_iterations <= 0:
        raise ValueError("Max iterations should be greater than 0")


def promethee_cluster_validation(alternatives_performances: pd.DataFrame,
                                 preference_thresholds: pd.Series,
                                 indifference_thresholds: pd.Series,
                                 standard_deviations: pd.Series,
                                 generalized_criteria: pd.Series,
                                 directions: pd.Series,
                                 weights: pd.Series,
                                 n_clusters: int):
    """
    Check if inputs are valid for PROMETHEE Cluster method.

    :param alternatives_performances: pd.DataFrame with alternatives as index
    and criteria as columns
    :param preference_thresholds: pd.Series with criteria as index and
    preference thresholds as values
    :param indifference_thresholds: pd.Series with criteria as index and
    indifference thresholds as values
    :param standard_deviations: pd.Series with criteria as index and
    standard deviations as values
    :param generalized_criteria: pd.Series with criteria as index and
    Generalized Criterion objects as values
    :param directions: pd.Series with criteria as index and
    Direction objects as values
    :param weights: pd.Series with criteria as index and
    weights as values
    :param n_clusters: number of clusters
    :raise ValueError: if any input is not valid
    """

    intervalp2clust_validation(alternatives_performances,
                               preference_thresholds,
                               indifference_thresholds,
                               standard_deviations,
                               generalized_criteria,
                               directions,
                               weights,
                               n_clusters)


def promethee_II_ordered_clustering_validation(
        alternatives_performances: pd.DataFrame,
        preference_thresholds: pd.Series,
        indifference_thresholds: pd.Series,
        standard_deviations: pd.Series,
        generalized_criteria: pd.Series,
        directions: pd.Series,
        weights: pd.Series,
        n_clusters: int):
    """
    Check if inputs are valid for PROMETHEE II Ordered Clustering method.

    :param alternatives_performances: pd.DataFrame with alternatives as index
    and criteria as columns
    :param preference_thresholds: pd.Series with criteria as index and
    preference thresholds as values
    :param indifference_thresholds: pd.Series with criteria as index and
    indifference thresholds as values
    :param standard_deviations: pd.Series with criteria as index and
    standard deviations as values
    :param generalized_criteria: pd.Series with criteria as index and
    Generalized Criterion objects as values
    :param directions: pd.Series with criteria as index and
    Direction objects as values
    :param weights: pd.Series with criteria as index and
    weights as values
    :param n_clusters: number of clusters
    :raise ValueError: if any input is not valid
    """

    intervalp2clust_validation(alternatives_performances,
                               preference_thresholds,
                               indifference_thresholds,
                               standard_deviations,
                               generalized_criteria,
                               directions,
                               weights,
                               n_clusters)


def intervalp2clust_validation(alternatives_performances: pd.DataFrame,
                               preference_thresholds: pd.Series,
                               indifference_thresholds: pd.Series,
                               standard_deviations: pd.Series,
                               generalized_criteria: pd.Series,
                               criteria_directions: pd.Series,
                               criteria_weights: pd.Series,
                               n_clusters: int,
                               max_iterations: int = 100):
    """
    Check if inputs are valid for Interval P2Clust method.

    :param alternatives_performances: pd.DataFrame with alternatives as index
    and criteria as columns
    :param preference_thresholds: pd.Series with criteria as index and
    preference thresholds as values
    :param indifference_thresholds: pd.Series with criteria as index and
    indifference thresholds as values
    :param standard_deviations: pd.Series with criteria as index and
    standard deviations as values
    :param generalized_criteria: pd.Series with criteria as index and
    Generalized Criterion objects as values
    :param criteria_directions: pd.Series with criteria as index and
    Direction objects as values
    :param criteria_weights: pd.Series with criteria as index and
    weights as values
    :param n_clusters: number of clusters
    :param max_iterations: number of max iterations
    :raise ValueError: if any input is not valid
    """

    _check_alternatives_performances(alternatives_performances)
    _check_preference_thresholds(preference_thresholds,
                                 criteria_weights.index)
    _check_indifference_thresholds(indifference_thresholds,
                                   criteria_weights.index)
    _check_standard_deviations(standard_deviations,
                               criteria_weights.index)
    _check_generalized_criteria(generalized_criteria)
    _check_criteria_directions(criteria_directions)
    _check_weights(criteria_weights)
    _check_n_clusters(alternatives_performances, n_clusters)
    _check_max_iterations(max_iterations)

    _check_preference_thresholds_better_than_indifference_thresholds(
        preference_thresholds, indifference_thresholds)
    _check_if_all_inputs_have_the_same_criteria(alternatives_performances,
                                                preference_thresholds,
                                                indifference_thresholds,
                                                standard_deviations,
                                                generalized_criteria,
                                                criteria_directions,
                                                criteria_weights)


def ordered_clustering_validation(alternatives_performances: pd.DataFrame,
                                  n_clusters: int):
    """
    Check if inputs are valid for Ordered Clustering method.

    :param alternatives_performances: pd.DataFrame with alternatives as index
    and criteria as columns
    :param n_clusters: number of clusters
    :raise ValueError: if any input is not valid
    """
    _check_alternatives_performances(alternatives_performances)
    _check_n_clusters(alternatives_performances, n_clusters)
