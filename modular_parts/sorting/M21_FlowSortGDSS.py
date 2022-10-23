import pandas as pd

from typing import List, Tuple, Dict
from enum import Enum
from core.preference_commons import directed_alternatives_performances
import numpy as np


class CompareProfiles(Enum):
    """Enumeration of the compare profiles types."""

    CENTRAL_PROFILES = 1
    BOUNDARY_PROFILES = 2


class FlowSortGDSS:
    """
    This module computes the assignments of given alternatives to categories using FlowSort GDSS procedure.
    """

    def __init__(self,
                 alternatives_general_net_flows: pd.Series,  # M21x
                 profiles_general_net_flows: pd.DataFrame,  # M21x
                 categories: List[str],
                 criteria_directions: pd.Series,
                 profiles_performances: List[pd.DataFrame],  # at least 2
                 DMs_weights: pd.Series,  # at least 2
                 comparison_with_profiles: CompareProfiles,
                 assign_to_better_class: bool = True
                 ):
        """
        :param alternatives_general_net_flows: Series with alternatives general net flows
        :param profiles_general_net_flows: DataFrame with profiles general net flows (index: (DM, profile),
         columns: alternatives)
        :param categories: List of categories names (strings only)
        :param profiles_performances: List with DataFrames with profiles performances for each DM
        :param DMs_weights: Series with weight of each DM
        :param comparison_with_profiles: Enum CompareProfiles - indicate information of profiles types used
        in calculation.
        :param assign_to_better_class: Boolean which describe preference of the DMs in final alternative assignment when
        distances to worse and better class are equal.
        """
        self.alternatives = alternatives_general_net_flows.index
        self.categories = categories
        self.profiles = profiles_performances[0].index
        self.DMs = profiles_general_net_flows.index.get_level_values(0)
        self.criteria_directions = criteria_directions
        self.alternatives_general_net_flows = alternatives_general_net_flows  # M21x
        self.profiles_general_net_flows = profiles_general_net_flows  # M21x
        self.profiles_performances = [directed_alternatives_performances(
            single_DM_profiles_performances, criteria_directions)
            for single_DM_profiles_performances in profiles_performances]
        self.DMs_weights = DMs_weights
        self.comparison_with_profiles = comparison_with_profiles
        self.assign_to_better_class = assign_to_better_class

        self.__check_dominance_condition()

    def __check_dominance_condition(self):
        """
        Check if each boundary profile is strictly worse in each criterion than betters profiles (even from other DM's)

        :raise ValueError: if any profile is not strictly worse in any criterion than any better profile
        """
        for criterion in self.criteria_directions.index:
            for DM_i_profiles_performances in self.profiles_performances:
                for i in range(len(self.profiles) - 1):
                    profile_i = DM_i_profiles_performances.iloc[i]
                    for DM_j_profiles_performances in self.profiles_performances:
                        profile_j = DM_j_profiles_performances.iloc[i + 1]
                        if profile_i[criterion] >= profile_j[criterion]:
                            raise ValueError("Each profile needs to be preferred over profiles which are worse than it,"
                                             " even they are from different DMs")

    def __classify_alternative(self, classification: pd.DataFrame,
                               not_classified: Dict[str, Dict[str, List[str]]],
                               alternative_assignment: pd.Series):
        """
        Classify (or no) alternative to proper category. Used in first step of assignment.

        :param classification: DataFrame with already done imprecise assignments (columns: 'worse', 'better')
        :param not_classified: Dictionary with alternatives which are not precisely classified yet
        :param alternative_assignment: Series with alternative assignment of each DM

        :return: Tuple with updated classification(DataFrame) and not_classified Dictionary
        """
        if alternative_assignment.nunique() > 1:
            worse_category, better_category = sorted(alternative_assignment.unique(),
                                                     key=lambda x: self.categories.index(x))

            DMs_that_chose_worse_category = alternative_assignment[alternative_assignment == worse_category].index
            DMs_that_chose_better_category = alternative_assignment[alternative_assignment == better_category].index

            not_classified[str(alternative_assignment.name)] = {'worse_category_voters': DMs_that_chose_worse_category,
                                                                'better_category_voters': DMs_that_chose_better_category}

            classification.loc[alternative_assignment.name, 'worse'] = worse_category
            classification.loc[alternative_assignment.name, 'better'] = better_category
        else:
            classification.loc[alternative_assignment.name, 'worse'] = alternative_assignment.unique()[0]
            classification.loc[alternative_assignment.name, 'better'] = alternative_assignment.unique()[0]

        return classification, not_classified

    def __calculate_first_step_assignments(self) -> Tuple[pd.DataFrame, Dict[str, Dict[str, List[str]]]]:
        """
        Use first step of assignment of FlowSort GDSS method to classify alternatives.
        Calculate assignment of each DM for each alternative. If alternative assignment is not unanimous adds this
        alternative to not_classified list.

        :return: Tuple with imprecise classification DataFrame and not_classified Dictionary
        """

        classification = pd.DataFrame(index=self.alternatives, columns=['better', 'worse'], dtype=str)
        not_classified = {}

        for alternative, alternative_general_net_flow, (_, profiles_general_net_flows_for_alternative) in zip(
                self.alternatives_general_net_flows.items(), self.profiles_general_net_flows.items()):
            alternative_assignments = pd.Series(index=self.DMs, dtype=str, name=alternative)
            for DM, DM_profiles_general_net_flows_for_alternative in \
                    profiles_general_net_flows_for_alternative.groupby(level=0):

                if self.comparison_with_profiles == CompareProfiles.BOUNDARY_PROFILES:
                    for profile_i, profile_net_flow in enumerate(DM_profiles_general_net_flows_for_alternative.values):
                        if profile_i == 0 and alternative_general_net_flow <= profile_net_flow:
                            alternative_assignments[DM] = self.categories[0]
                            break
                        elif profile_i == len(self.profiles) - 1 and alternative_general_net_flow > profile_net_flow:
                            alternative_assignments[DM] = self.categories[-1]
                            break
                        elif alternative_general_net_flow <= profile_net_flow:
                            alternative_assignments[DM] = self.categories[profile_i]
                            break
                else:
                    profile_distances = [abs(profile_net_flow - alternative_general_net_flow) for profile_net_flow in
                                         DM_profiles_general_net_flows_for_alternative.values]
                    category_index = np.argmin(profile_distances)
                    alternative_assignments[DM] = self.categories[category_index]

            classification, not_classified = self.__classify_alternative(classification, not_classified,
                                                                         alternative_assignments)

        return classification, not_classified

    def __calculate_final_assignments(self, classification: pd.DataFrame,
                                      not_classified: Dict[str, Dict[str, List[str]]]):
        """
        Use final step of assignment to classify alternatives which could not be classified in first step of assignment.
        Calculates distance to worse and better category based on DM's decision and DM's alternative profile net flows.
        Then classifies alternative to category which has smaller distance to it. If distances are the same,
         alternative is classified by using class param 'assign_to_better_class'.

        :param classification: DataFrame with imprecise assignments (columns: 'worse', 'better')
        :param not_classified: Dictionary with alternatives which are not precisely classified yet

        :return: Series with precise classification.
        """
        final_classification = classification.copy()

        for alternative, voters in not_classified.items():

            worse_category_voters = voters['worse_category_voters']
            better_category_voters = voters['better_category_voters']

            worse_category = classification.loc[alternative, 'worse']
            better_category = classification.loc[alternative, 'better']

            worse_category_voters_weights = self.DMs_weights[worse_category_voters]
            worse_category_profile = self.profiles[self.categories.index(worse_category)]
            worse_category_profiles_general_net_flows = \
                self.profiles_general_net_flows.loc[(worse_category_voters, worse_category_profile), alternative]

            better_category_voters_weights = self.DMs_weights[better_category_voters]
            better_category_profile = self.profiles[min(self.categories.index(
                better_category), len(self.profiles) - 1)]
            better_category_profiles_general_net_flows = \
                self.profiles_general_net_flows.loc[(better_category_voters, better_category_profile), alternative]

            if self.comparison_with_profiles == CompareProfiles.BOUNDARY_PROFILES:
                worse_category_distance = np.sum(
                    (self.alternatives_general_net_flows[alternative] - worse_category_voters_weights) *
                    worse_category_profiles_general_net_flows)

                better_category_distance = np.sum(
                    (better_category_voters_weights - self.alternatives_general_net_flows[alternative]) *
                    better_category_profiles_general_net_flows)

            else:
                worse_category_distance = np.sum(
                    (worse_category_voters_weights - self.alternatives_general_net_flows[alternative]).abs() *
                    worse_category_profiles_general_net_flows)

                better_category_distance = np.sum(
                    (better_category_voters_weights - self.alternatives_general_net_flows[alternative]).abs() *
                    better_category_profiles_general_net_flows)

            if better_category_distance > worse_category_distance:
                final_classification.loc[alternative, 'better'] = worse_category
            elif better_category_distance < worse_category_distance:
                final_classification.loc[alternative, 'worse'] = better_category
            else:
                if self.assign_to_better_class:
                    final_classification.loc[alternative, 'worse'] = better_category
                else:
                    final_classification.loc[alternative, 'better'] = worse_category

        final_classification = final_classification['better']

        return final_classification

    def calculate_sorted_alternatives(self) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Sort alternatives to proper categories.

        :return: DataFrame with imprecise assignments (columns: 'worse', 'better') and Series with precise assignments.
        """
        first_step_assignments, not_classified = self.__calculate_first_step_assignments()
        final_step_assignments = self.__calculate_final_assignments(first_step_assignments, not_classified)

        return first_step_assignments, final_step_assignments
