import random
from typing import Any, Union
import pandas as pd
from collections import defaultdict
from core.enums import Direction


def group_alternatives(assignment: pd.Series) -> pd.Series:
    """
    Converts output from Promethee Tri module into
    pd.Series with clusters as indexes assignment by numbers of assigned
    alternatives.

    :param assignment: Series with precise assignments of alternatives to
        categories

    :return: Series with alternatives grouped into k ordered clusters
    """
    cluster = pd.Series([], dtype=pd.StringDtype())
    for key, value in assignment.items():
        if value in cluster:
            cluster[value].append(key)
        else:
            cluster[value] = [key]
    return cluster


def calculate_new_profiles(profiles_performances: pd.DataFrame,
                           alternatives_performances: pd.DataFrame,
                           assignment: Union[pd.DataFrame, pd.Series],
                           method: Any) -> pd.DataFrame:
    """
    Redefines profiles_performances' performances based on alternatives
    assigned to it.

    :param profiles_performances: DataFrame of profiles' performances
    :param alternatives_performances: DataFrame of alternatives' performances
    :param assignment: Series with precise assignments of alternatives to
        categories
    :param method: Math method used for profiles' redefinition.

    :return: Dataframe with redefined profiles' performances
    """
    central_profiles_out = profiles_performances.copy(deep=True)
    profile_alternatives = defaultdict(list)
    for index, value in assignment.items():
        profile_alternatives[value].append(index)
    for profile in central_profiles_out.index:
        for criterion in central_profiles_out.columns:
            if profile in profile_alternatives.keys():
                method_value = method(alternatives_performances.loc[
                                          profile_alternatives[
                                              profile], criterion])
                central_profiles_out.loc[profile, criterion] = method_value
    return central_profiles_out


def initialize_the_central_profiles(
        alternatives_performances: pd.DataFrame,
        categories: pd.Index,
        directions: pd.Series) -> pd.DataFrame:
    """
    First step of clustering. Initialization of the central
    profiles. Profiles features have random values, but they
    keep the rule of not being worse than the worse profile.

    :param alternatives_performances: DataFrame of alternatives' performances
    :param categories: Categories' indices
    :param directions: directions of preference of criteria

    :return: New DataFrame of profiles' performances
    """
    min_and_max_performances = pd.DataFrame(
        {'Min': alternatives_performances.min(),
         'Max': alternatives_performances.max()})
    central_profiles = pd.DataFrame(index=categories, dtype=float)
    for criterion, direction in zip(alternatives_performances.columns,
                                    directions):
        performances = []
        for _ in categories:
            value = random.uniform(
                min_and_max_performances.loc[criterion, 'Min'],
                min_and_max_performances.loc[criterion, 'Max'])
            while value in performances:
                value = random.uniform(
                    min_and_max_performances.loc[criterion, 'Min'],
                    min_and_max_performances.loc[criterion, 'Max'])
            performances.append(value)

        reverse = (direction == Direction.MIN)
        central_profiles[criterion] = sorted(performances, reverse=reverse)

    return central_profiles
