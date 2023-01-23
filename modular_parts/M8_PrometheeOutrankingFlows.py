"""
    .. image:: prometheePUT_figures/M8.jpg

    This module computes the outranking flows if basic(PROMETHEE I) or
    profile-based style.

    Implementation and naming of conventions are taken from
    :cite:p:`BransMareschal2005`.
"""
from typing import Tuple, Union, cast

import pandas as pd

from core.enums import FlowType

__all__ = ["calculate_promethee_outranking_flows"]

from core.input_validation.flow import (
    basic_outranking_flows_validation,
    check_outranking_flows_type,
    profile_based_outranking_flows_validation,
)


def _calculate_flow(
    preferences: Union[Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame],
    positive: bool = True,
) -> pd.Series:
    """
    Calculate positive or negative outranking flow in basic(PROMETHEE I)
     style.

    :param preferences: pd.DataFrame with alternatives as index and
        alternatives as columns or Tuple of pd.DataFrame with alternatives as
        index and profiles as columns and pd.DataFrame with profiles as index
        and alternatives as columns.
    :param positive: bool, if True function returns positive outranking flow
        else returns negative outranking flow.
    :return: pd.Series with alternatives as index and positive or
        negative flows are values.
    """
    if isinstance(preferences, tuple):
        if positive:
            flows = preferences[0].mean(axis=1)
        else:
            flows = preferences[1].mean(axis=0)
        return flows
    else:
        # Current alternative is not took into account
        # (btw. its inner preference is 0)
        axis = 1 if positive else 0
        aggregated_preferences = preferences.sum(axis=axis) / (preferences.shape[0] - 1)

        return aggregated_preferences


def _calculate_profile_based_flow(
    preferences: Tuple[pd.DataFrame, pd.DataFrame],
    profiles_preferences: pd.DataFrame,
    positive: bool = True,
) -> pd.Series:
    """
    Calculate positive or negative outranking profile-based flows.

    :param preferences: Tuple of pd.DataFrame with alternatives as index
        and profiles as columns and pd.DataFrame with profiles as index
        and alternatives as columns.
    :param profiles_preferences: pd.DataFrame with profiles as index and
        profiles as columns.
        bool, if True function returns positive outranking flow
        else returns negative outranking flow.
    :return: pd.Series with
        MultiIndex("R" + alternatives, profiles + alternative) as index and
        positive or negative flows are values.
    """
    n_profiles = len(profiles_preferences)
    alternatives_groups_flows = []
    alternatives_groups_names = []
    axis = 1 if positive else 0

    # Iterate over alternatives
    for alternative, alternative_preferences in preferences[0].iterrows():
        # Create subset of profiles + current alternative preferences

        # Copy profiles preferences
        alternative_group_preferences = profiles_preferences.copy()
        # Add current alternative preferences to the end of
        # the subset (row and column)
        alternative_group_preferences.loc[alternative] = alternative_preferences
        alternative_group_preferences[alternative] = preferences[1][alternative]

        # Calculate flows for current group
        alternatives_groups_flows.append(
            alternative_group_preferences.sum(axis=axis) / n_profiles
        )
        alternatives_groups_names.append(f"R{alternative}")

    # Combine all groups flows
    return pd.concat(alternatives_groups_flows, keys=alternatives_groups_names)


def calculate_promethee_outranking_flows(
    preferences: Union[Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame],
    flow_type: FlowType,
    profiles_preferences: pd.DataFrame = None,
) -> pd.DataFrame:
    """
    Calculate outranking flows in basic(PROMETHEE I) or profile-based style.
    Basic(PROMETHEE I) flows are calculated as mean of subtractions of
    preferences where current alternative is preferred to
    profiles/alternatives and preferences where profiles/alternatives
    is preferred to current alternative.
    Profile-based flows are calculated by creating
    subsets: profiles + current alternative and calculating flows in that
    set as in basic style. Because of modularity of this project
    preferences for that flows are obtained in different way (needs
    alternatives vs profiles and profiles vs profiles preferences).

    :param preferences: pd.DataFrame with alternatives as index and
        alternatives as columns or Tuple of pd.DataFrame with alternatives as
        index and alternatives as columns and pd.DataFrame with profiles as
        index and alternatives as columns.
    :param flow_type: FlowType enum with type of outranking
        flows (BASIC OR PROFILE_BASED).
    :param profiles_preferences: pd.DataFrame with profiles as index and
        profiles as columns.
    :return: pd.DataFrame with alternatives as index and 'positive' and
        'negative' columns if flow_type is BASIC or pd.DataFrame with
        MultiIndex("R" + alternatives, profiles+alternative) as index and
        'positive' and 'negative' columns if flow_type is PROFILE_BASED.
    """

    # flow_type validation
    check_outranking_flows_type(flow_type)

    if flow_type == FlowType.BASIC:
        # Input validation for basic(PROMETHEE I) style
        basic_outranking_flows_validation(preferences)

        # Get alternatives as index
        index = (
            preferences[0].index
            if isinstance(preferences, tuple)
            else preferences.index
        )
        return pd.DataFrame(
            {
                "positive": _calculate_flow(preferences),
                "negative": _calculate_flow(preferences, positive=False),
            },
            index=index,
        )

    else:  # flow_type == FlowType.PROFILE_BASED:
        # Input validation for profile-based style
        profiles_preferences = cast(pd.DataFrame, profiles_preferences)
        preferences = cast(Tuple[pd.DataFrame, pd.DataFrame], preferences)
        profile_based_outranking_flows_validation(preferences, profiles_preferences)
        return pd.DataFrame(
            {
                "positive": _calculate_profile_based_flow(
                    preferences, profiles_preferences
                ),
                "negative": _calculate_profile_based_flow(
                    preferences, profiles_preferences, positive=False
                ),
            }
        )
