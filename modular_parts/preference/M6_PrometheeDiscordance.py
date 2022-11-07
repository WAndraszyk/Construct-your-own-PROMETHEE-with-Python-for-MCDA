import pandas as pd
from typing import List
from core.aliases import NumericValue
from core.preference_commons import overall_preference

__all__ = ["compute_discordance"]


def compute_discordance(criteria: List[str], partial_preferences: pd.DataFrame, tau: NumericValue,
                        preferences: pd.DataFrame = None,
                        categories_profiles=False) -> tuple[pd.DataFrame | List[pd.DataFrame], pd.DataFrame |
                                                            List[pd.DataFrame]] | pd.DataFrame | tuple[pd.DataFrame]:
    """
    Calculates overall discordance by aggregating partial discordance indices.

    :param tau: technical parameter, τ ∈ [1, k], smaller τ → weaker discordance
    :param preferences: if not empty function returns already calculated preference instead of just discordance
    :param criteria: list of criteria names
    :param partial_preferences: partial preference of every alternative over other alternatives or profiles
    :param categories_profiles: were the preferences calculated for profiles

    :return: matrix of overall discordance and matrix of partial discordance indices. Alternatively: preference
    """

    criteria = criteria
    categories_profiles = categories_profiles
    partial_preferences = partial_preferences
    if tau < 1 or tau > len(criteria):
        raise Exception("Tau needs to be a number from 1 to k, where k is the number of criteria.")

    if not categories_profiles:
        partial_discordance = _calculate_partial_discordance(criteria, partial_preferences)
        discordance = _overall_discordance(criteria, partial_discordance, tau)
    else:
        partial_discordance = [
            _calculate_partial_discordance(criteria, partial_preferences[0], partial_preferences[1]),
            _calculate_partial_discordance(criteria, partial_preferences[1], partial_preferences[0])]
        discordance = []
        for i in partial_discordance:
            discordance.append(_overall_discordance(criteria, i, tau))

    if preferences is not None:
        return overall_preference(preferences, discordance, categories_profiles)
    else:
        return discordance, partial_discordance


def _calculate_partial_discordance(criteria: List[str], partial_preferences: pd.DataFrame,
                                   other_partial_preferences: pd.DataFrame = None) -> pd.DataFrame:
    """
    Calculates partial discordance indices based on partial preference indices

    :param partial_preferences: partial preference of every alternative over other alternatives
    or profiles

    :returns: 3D matrix of partial discordance indices
    """
    if other_partial_preferences is None:
        other_partial_preferences = partial_preferences

    partial_discordance_data = []

    for criterion in criteria:
        partial_discordance_on_criterion = other_partial_preferences.loc[criterion].T
        partial_discordance_data.append(partial_discordance_on_criterion)

    partial_discordance = pd.concat(partial_discordance_data, axis=0, keys=criteria)

    return partial_discordance


def _overall_discordance(criteria: List[str], partial_discordance: pd.DataFrame, tau: NumericValue) -> pd.DataFrame:
    """
    Calculates overall discordance by aggregating partial discordance indices.

    :param partial_discordance: matrix of partial discordance indices
    :param tau: technical parameter, τ ∈ [1, k], smaller τ → weaker discordance
    :return: matrix of overall discordance
    """
    discordance = []
    k = len(criteria)
    index = partial_discordance.loc[criteria[0]].index
    columns = partial_discordance.loc[criteria[0]].columns
    for i in index:
        aggregated_discordance = []
        for column in columns:
            D_a_b = 1
            for criterion in criteria:
                D_a_b *= pow(1 - partial_discordance.loc[criterion, i][column], tau / k)
            D_a_b = 1 - D_a_b
            aggregated_discordance.append(D_a_b)
        discordance.append(aggregated_discordance)

    return pd.DataFrame(data=discordance, index=index, columns=columns)
