import pandas as pd

from core.enums import GeneralCriterion, Direction
from core.input_validation import _check_if_dataframe

__all__ = ["pclust_validation", "ordered_clustering_validation", "promethee_II_ordered_clustering_validation",
           "promethee_cluster_validation"]


def _check_alternatives_performances(alternatives_performances: pd.DataFrame):
    if not isinstance(alternatives_performances, pd.DataFrame):
        raise ValueError("Alternatives performances should be passed as a DataFrame")
    if not alternatives_performances.dtypes.values.all() in ['int64', 'float64']:
        raise ValueError("Alternatives performances should be passed with int or float values")


def _check_thresholds(thresholds: pd.Series, thresholds_name: str):
    if not isinstance(thresholds, pd.Series):
        raise ValueError(f"{thresholds_name} should be passed as a Series")
    if not thresholds.dtypes in ['float64', 'int64']:
        raise ValueError(f"{thresholds_name} should be passed with float values")
    if not thresholds.all() >= 0:
        raise ValueError(f"{thresholds_name} should be passed with values greater or equal to 0")


def _check_generalized_criteria(generalized_criteria: pd.Series):
    if not isinstance(generalized_criteria, pd.Series):
        raise ValueError("Generalized criteria should be passed as a Series")
    if not (generalized_criteria.values.all() in [GeneralCriterion.USUAL, GeneralCriterion.U_SHAPE,
                                                  GeneralCriterion.V_SHAPE, GeneralCriterion.LEVEL,
                                                  GeneralCriterion.V_SHAPE_INDIFFERENCE,
                                                  GeneralCriterion.GAUSSIAN]):
        raise ValueError("Generalized criteria should be core.enums.PreferenceFunction enums")


def _check_criteria_directions(criteria_directions: pd.Series):
    if not isinstance(criteria_directions, pd.Series):
        raise ValueError("Criteria directions should be a Series object")

    if criteria_directions.values.any() not in [Direction.MAX, Direction.MIN]:
        raise ValueError("Criteria directions should be core.enums.Direction enums")


def _check_weights(weights: pd.Series, criteria_num: int):
    if not isinstance(weights, pd.Series):
        raise ValueError("Criteria weights should be passed as a Series object")

    if len(weights) != criteria_num:
        raise ValueError("Number of weights should be equals to number of criteria")

    for weight in weights:
        if not isinstance(weight, (int, float)):
            raise ValueError("Weights should be a numeric values")

    if (weights <= 0).any():
        raise ValueError("Weights should be positive")


def _check_preference_thresholds_better_than_indifference_thresholds(preference_thresholds: pd.Series,
                                                                     indifference_thresholds: pd.Series):
    if (preference_thresholds[preference_thresholds < indifference_thresholds] != 0).any():
        raise ValueError("Preference thresholds should be greater than indifference thresholds")


def _check_if_all_object_have_the_same_criteria(alternatives_performances: pd.DataFrame,
                                                preference_thresholds: pd.Series,
                                                indifference_thresholds: pd.Series,
                                                standard_deviations: pd.Series,
                                                generalized_criteria: pd.Series,
                                                criteria_directions: pd.Series,
                                                criteria_weights: pd.Series):
    if not (alternatives_performances.columns.all() == preference_thresholds.index.all() ==
            preference_thresholds.index.all() == indifference_thresholds.index.all() ==
            standard_deviations.index.all() == generalized_criteria.index.all() ==
            criteria_directions.index.all() == criteria_weights.index.all()):
        raise ValueError("All objects should have the same criteria")


def _check_n_categories(alternatives_performances: pd.DataFrame,
                        categories: int):
    if alternatives_performances.shape[0] <= categories:
        raise ValueError("Number of categories should be lower than number of alternatives")

    if categories < 2:
        raise ValueError("Number of categories should be greater than 1")


def _check_max_iterations(number_of_iterations: int):
    if not isinstance(number_of_iterations, int):
        raise ValueError("Max iterations should be passed as an integer")
    if number_of_iterations <= 0:
        raise ValueError("Max iterations should be greater than 0")


def promethee_cluster_validation(alternatives_performances: pd.DataFrame,
                                 preference_thresholds: pd.Series,
                                 indifference_thresholds: pd.Series,
                                 standard_deviations: pd.Series,
                                 generalized_criteria: pd.Series,
                                 directions: pd.Series,
                                 weights: pd.Series,
                                 n_categories: int):
    pclust_validation(alternatives_performances,
                      preference_thresholds,
                      indifference_thresholds,
                      standard_deviations,
                      generalized_criteria,
                      directions,
                      weights,
                      n_categories)


def promethee_II_ordered_clustering_validation(alternatives_performances: pd.DataFrame,
                                               preference_thresholds: pd.Series,
                                               indifference_thresholds: pd.Series,
                                               standard_deviations: pd.Series,
                                               generalized_criteria: pd.Series,
                                               directions: pd.Series,
                                               weights: pd.Series,
                                               n_categories: int):
    pclust_validation(alternatives_performances,
                      preference_thresholds,
                      indifference_thresholds,
                      standard_deviations,
                      generalized_criteria,
                      directions,
                      weights,
                      n_categories)


def pclust_validation(alternatives_performances: pd.DataFrame,
                      preference_thresholds: pd.Series,
                      indifference_thresholds: pd.Series,
                      standard_deviations: pd.Series,
                      generalized_criteria: pd.Series,
                      criteria_directions: pd.Series,
                      criteria_weights: pd.Series,
                      n_categories: int,
                      max_iterations: int = 100):
    _check_alternatives_performances(alternatives_performances)
    _check_thresholds(preference_thresholds, "Preference thresholds")
    _check_thresholds(indifference_thresholds, "Indifference thresholds")
    _check_thresholds(standard_deviations, "Standard deviations")
    _check_generalized_criteria(generalized_criteria)
    _check_criteria_directions(criteria_directions)
    _check_weights(criteria_weights, len(criteria_directions))
    _check_n_categories(alternatives_performances, n_categories)
    _check_max_iterations(max_iterations)

    _check_preference_thresholds_better_than_indifference_thresholds(preference_thresholds, indifference_thresholds)
    _check_if_all_object_have_the_same_criteria(alternatives_performances, preference_thresholds,
                                                indifference_thresholds, standard_deviations,
                                                generalized_criteria, criteria_directions,
                                                criteria_weights)


def _check_cluster_no(clusters_no: int):
    if not isinstance(clusters_no, int):
        raise TypeError("Number of clusters should be an integer")
    if clusters_no <= 0:
        raise ValueError("Number of clusters should be grater than 0")


def ordered_clustering_validation(preferences: pd.DataFrame, clusters_no: int):
    _check_if_dataframe(preferences, "Preferences")
    _check_cluster_no(clusters_no)
