import pandas as pd
from typing import List
from core.preference_commons import directed_alternatives_performances


def check_dominance_condition(criteria_directions: pd.Series,
                              category_profiles: pd.DataFrame):
    """
    Check if each boundary profile is strictly worse on each criterion
    than betters profiles

    :param criteria_directions: pd.Series with criteria as index and
    Direction as values
    :param category_profiles: pd.DataFrame with profiles as index and criteria
    as columns
    :raise ValueError: if any profile is not strictly worse in any
    criterion than anny better profile
    """
    directed_category_profiles = directed_alternatives_performances(
        category_profiles, criteria_directions)

    for (criterion, _) in criteria_directions.items():
        for i, (_, profile_i) in enumerate(
                directed_category_profiles.iloc[:-1].iterrows()):
            profile_j = directed_category_profiles.iloc[i + 1]
            if profile_j[criterion] < profile_i[criterion]:
                raise ValueError("Profiles don't fulfill "
                                 "the dominance condition")


def check_dominance_condition_GDSS(profiles: pd.Index,
                                   profiles_performances: List[pd.DataFrame],
                                   criteria_directions: pd.Series):
    """
    Check if each boundary profile is strictly worse in each criterion
    than betters profiles (even from other DM's).

    :param profiles: pd.Index with profiles names
    :param profiles_performances: List with pd.DataFrame objects with profiles
    as index and criteria as columns
    :param criteria_directions: pd.Series with criteria as index and
    Direction as values

    :raise ValueError: if any profile is not strictly worse on any
    criterion than any better profile
    """
    for criterion in criteria_directions.index:
        for DM_i_profiles_performances in profiles_performances:
            for i in range(len(profiles) - 1):
                profile_i = DM_i_profiles_performances.iloc[i]
                for DM_j_profiles_performances in profiles_performances:
                    profile_j = DM_j_profiles_performances.iloc[i + 1]
                    if profile_i[criterion] >= profile_j[criterion]:
                        raise ValueError("Each profile needs to be preferred "
                                         "over profiles which are worse than "
                                         "it, even they are from different "
                                         "DMs")


def check_if_profiles_are_strictly_worse(criteria_thresholds: pd.Series,
                                         category_profiles: pd.DataFrame):
    """
    Check if each boundary profile is strictly worse in each criterion
    by specified threshold than betters profiles.

    :param criteria_thresholds: pd.Series with criteria as index and
    thresholds as values
    :param category_profiles: pd.DataFrame with profiles as index and criteria
    as columns

    :raise ValueError: if any profile is not strictly worse on any criterion
    than anny better profile
    """
    for criterion, threshold in criteria_thresholds.items():
        for i, (_, profile_i) in enumerate(
                category_profiles.iloc[:-1].iterrows()):
            profile_j = category_profiles.iloc[i + 1]
            if profile_i[criterion] + threshold > profile_j[criterion]:
                raise ValueError("Each profile needs to be preferred over "
                                 "profiles which are worse than it")
