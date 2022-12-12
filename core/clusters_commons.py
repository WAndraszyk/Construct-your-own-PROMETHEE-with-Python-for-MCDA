import random
from typing import Any, Union

import pandas as pd
from collections import defaultdict


def group_alternatives(assignment: pd.Series) -> pd.Series:
    """
    Converts output form @calculate_prometheetri_sorted_alternatives to
    cluster.

    :param assignment: Series of alternatives assignment

    :return: Series of alternatives grouped into clusters

    """
    cluster = pd.Series([], dtype=pd.StringDtype())
    for key, value in assignment.iteritems():
        if value in cluster:
            cluster[value].append(key)
        else:
            cluster[value] = [key]
    return cluster


def calculate_new_profiles(profiles_performances: pd.DataFrame,
                           alternatives_performances: pd.DataFrame,
                           sorted: Union[pd.DataFrame, pd.Series],
                           function: Any) -> pd.DataFrame:
    """
    This function redefines profiles' performances on the basis of the
    alternatives belonging to it using math @function.


    :param central_profiles: DataFrame of profiles' performances
    :param alternatives_performances: DataFrame of alternatives' performances
    :param sorted: Series of alternatives grouped into k ordered clusters
    :param function: math function used for profiles' redefinition

    :return: DataFrame of updated profiles' performance

    """
    central_profiles_out = profiles_performances.copy()
    profile_alternatives = defaultdict(list)
    for index, value in sorted.items():
        profile_alternatives[value].append(index)
    for profile in central_profiles_out.index:
        for criterion in central_profiles_out.columns:
            if profile in profile_alternatives.keys():
                method_value = function(alternatives_performances.loc[
                                          profile_alternatives[
                                              profile], criterion])
                central_profiles_out.loc[profile, criterion] = method_value
    return central_profiles_out


def initialization_of_the_central_profiles(
        alternatives_performances: pd.DataFrame,
        categories: pd.Index,
        directions: pd.Series) -> pd.DataFrame:
    """
    First step of clustering. Initialization of the central profiles.
    Profiles features have random values, but they keep the rule of not
    being worse than the worse profile.

    :param alternatives_performances: DataFrame of alternatives' performances
    :param categories: Indices of categories
    :param directions: directions of preference of criteria

    :return: new profiles' performances
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
        central_profiles[criterion] = sorted(performances)
    return central_profiles
