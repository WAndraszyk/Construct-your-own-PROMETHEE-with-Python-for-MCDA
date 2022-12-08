import random
import pandas as pd
from pandas._libs.internals import defaultdict
# from collections import defaultdict


def group_alternatives(assignment: pd.Series) -> pd.Series:
    """
    Converts output form @calculate_prometheetri_sorted_alternatives into pd.Series with clusters as indexes sorted by
    numbers of assigned alternatives .

    :return: Alternatives assignment, Redefined central_profiles

    """
    cluster = pd.Series([], dtype=pd.StringDtype())
    for key, value in assignment.iteritems():
        if value in cluster:
            cluster[value].append(key)
        else:
            cluster[value] = [key]
    return cluster


def calculate_new_profiles(central_profiles, alternatives_performances, sorted, method):
    """
    Redefines profile's performance based on alternatives assigned to it.

    :return: Redefined central_profiles

    """
    central_profiles_out = central_profiles.copy()
    profile_alternatives = defaultdict(list)
    for index, value in sorted.items():
        profile_alternatives[value].append(index)
    for profile in central_profiles_out.index:
        for criterion in central_profiles_out.columns:
            if profile in profile_alternatives.keys():
                method_value = method(alternatives_performances.loc[profile_alternatives[profile], criterion])
                central_profiles_out.loc[profile, criterion] = method_value
    return central_profiles_out


def initialization_of_the_central_profiles(alternatives_performances: pd.DataFrame,
                                           categories: pd.Index,
                                           directions: pd.Series) -> pd.DataFrame:
    """
    First step of clustering. Initialization of the central profiles. Profiles features have random values, but they
    keep the rule of not being worse than the worse profile.
    """
    min_and_max_performances = pd.DataFrame(
        {'Min': alternatives_performances.min(),
         'Max': alternatives_performances.max()})
    central_profiles = pd.DataFrame(index=categories, dtype=float)
    for criterion, direction in zip(alternatives_performances.columns, directions):
        performances = []
        for _ in categories:
            value = random.uniform(min_and_max_performances.loc[criterion, 'Min'],
                                   min_and_max_performances.loc[criterion, 'Max'])
            while value in performances:
                value = random.uniform(min_and_max_performances.loc[criterion, 'Min'],
                                       min_and_max_performances.loc[criterion, 'Max'])
            performances.append(value)
        central_profiles[criterion] = sorted(performances)
    return central_profiles
