import pandas as pd

from core.aliases import NumericValue, PerformanceTable, CriteriaFeatures, FlowsTable
from typing import List, Tuple
from core.preference_commons import directed_alternatives_performances


class PromSort:
    """
    This module computes the assignments of given alternatives to categories using PromSort.
    """

    def __init__(self,
                 categories: List[str],
                 category_profiles: PerformanceTable,
                 criteria: CriteriaFeatures,
                 alternatives_flows: FlowsTable,
                 category_profiles_flows: FlowsTable,
                 cut_point: NumericValue,  # <-1, 1>, used in second phase
                 assign_to_better_class: bool = True):
        """
        :param categories: List of categories names
        :param category_profiles: Performance table with category profiles performances
        :param criteria: Criteria features table with criteria direction and thresholds
        :param alternatives_flows: Flows table with alternatives flows
        :param category_profiles_flows: Flows table with category profiles flows
        :param cut_point: Numeric Value in range <-1, 1> which define DM preference of classifying alternative to worse
        or better class in final alternative assignment
        (-1 means 'always worse category', 1 means 'always better category')
        :param assign_to_better_class: Boolean which describe preference of the DM in final alternative assignment if
        total distance is equal cut_point value.
        """
        self.categories = categories
        self.category_profiles = pd.DataFrame(directed_alternatives_performances(category_profiles.values,
                                                                                 criteria['criteria_directions']),
                                              index=category_profiles.columns, columns=category_profiles.columns)
        self.criteria = criteria
        self.alternatives_flows = alternatives_flows
        self.category_profiles_flows = category_profiles_flows
        self.cut_point = cut_point
        self.assign_to_better_class = assign_to_better_class
        self.__check_if_profiles_are_strictly_worse()

    def __check_if_profiles_are_strictly_worse(self):
        """
        Check if each boundary profile is strictly worse in each criterion by specified threshold than betters profiles

        :raise ValueError: if any profile is not strictly worse in any criterion than anny better profile
        """
        for criterion, threshold in self.criteria['preference_thresholds'].items():
            for i, (_, profile_i) in enumerate(self.category_profiles.iloc[:-1].iterrows()):
                profile_j = self.category_profiles.iloc[i + 1]
                if profile_i[criterion] + threshold > profile_j[criterion]:
                    raise ValueError("Each profile needs to be preferred over profiles which are worse than it")

    @staticmethod
    def __define_outranking_relation(positive_flow_a: NumericValue, negative_flow_a: NumericValue,
                                     positive_flow_b: NumericValue, negative_flow_b: NumericValue) -> chr:
        """
        This function declare 3 types of outranking relation between alternative
        and profile or profile and alternative (preference - 'P', indifference - 'I', incomparable - '?')

        :param positive_flow_a: positive flow of first profile/alternative
        :param negative_flow_a: negative flow of first profile/alternative
        :param positive_flow_b: positive flow of second profile/alternative
        :param negative_flow_b: negative flow of second profile/alternative

        :return: one of three types of outranking relation between first profile/alternative and
        second profile/alternative
        """
        if positive_flow_a == positive_flow_b \
                and negative_flow_a == negative_flow_b:
            return "I"
        elif positive_flow_a >= positive_flow_b \
                and negative_flow_a <= negative_flow_b:
            return "P"
        else:
            return "?"

    def __check_if_all_profiles_are_preferred_to_alternative(self, alternative_positive_flow: NumericValue,
                                                             alternative_negative_flow: NumericValue) -> bool:
        """
        Checks if all profiles are preferred to alternative
        (which allow sorting method to assign alternative to the worst category)

        :param alternative_positive_flow: Numeric Value of positive flow of alternative
        :param alternative_negative_flow: Numeric Value of negative flow of alternative

        :return: True if all profiles are preferred to alternative, else False
        """
        outranking_relations = self.category_profiles_flows.apply(
            lambda row: self.__define_outranking_relation(row['positive_flow'], row['negative_flow'],
                                                          alternative_positive_flow, alternative_negative_flow), axis=1)
        return outranking_relations.str.contains('P').all()

    def __calculate_first_step_assignments(self) -> pd.DataFrame:
        """
        Calculates first step of assignments alternatives to categories.
        This function calculates outranking relations alternative to each boundary profile, then:
        - if alternative is preferred to all boundary profiles then assign alternative to the best category
        - calculate outranking relations of each boundary profile to alternative, if all boundary profiles are
        preferred to alternative then assign alternative to the worst category
        - if first incomparable or indifference appeared to the worse profile than first preference then assign
        alternative to first preference index + 1 category
        - else alternative is "not fully classified". This alternative will have assigned first incomparable
        or indifference index category as worse class and first incomparable or indifference index +1 category
         as better class.

        :return: Dictionary with classifications and List of Tuples of alternative, worse and better class to
        which can be alternative assigned in final assignments step
        """

        classification = {alternative: [] for alternative in self.alternatives_flows.index}

        for alternative, alternative_row in self.alternatives_flows.iterrows():
            outranking_relations = self.category_profiles_flows.apply(
                lambda category_profile_row: self.__define_outranking_relation(
                    alternative_row['positive'], alternative_row['negative'],
                    category_profile_row['positive'], category_profile_row['negative']), axis=1)

            first_I_occurrence = outranking_relations.str.contains('I').idxmax() if outranking_relations.str.contains(
                'I').any() else float('inf')
            first_R_occurrence = outranking_relations.str.contains('?').idxmax() if outranking_relations.str.contains(
                '?').any() else float('inf')
            last_P_occurrence = outranking_relations.str.contains('P').idxmin() if outranking_relations.str.contains(
                'P').any() else float('inf')

            if outranking_relations[-1] == 'P':
                classification[alternative] = [self.categories[-1], self.categories[-1]]
            elif self.__check_if_all_profiles_are_preferred_to_alternative(alternative_row['positive'],
                                                                           alternative_row['negative']):
                classification[alternative] = [self.categories[0], self.categories[0]]
            elif min(first_R_occurrence, first_I_occurrence) > last_P_occurrence:
                classification[alternative] = [self.categories[last_P_occurrence + 1],
                                                   self.categories[last_P_occurrence + 1]]
            else:
                min_idx = min(first_R_occurrence, first_I_occurrence)
                classification[alternative] = [self.categories[min_idx], self.categories[min_idx + 1]]

        return pd.DataFrame.from_dict(classification, orient='index', columns=['worse', 'better'])

    def __calculate_final_assignments(self, classification: pd.DataFrame) -> pd.Series:
        """
        Used assigned categories to assign the unassigned ones. Based on positive and negative distance,
        that is calculated for each alternative, basing on calculated in first step categories (s and s+1).
        After calculating positive and negative distances a total distance is determining.
        After computing the total distance for all alternatives and profiles it is compared with cut point parameter.

        :param classification: DataFrame with classifications of alternatives (worse and better class)

        :return: DataFrame with final classifications of alternatives (only one class)
        """

        new_classification = classification.apply(lambda row: row['worse'] if row['worse'] == row['better'] else None)
        not_classified = classification[new_classification.isnull()]
        classified = classification[~new_classification.isnull()]

        for alternative, alternative_row in not_classified.iterrows():
            worse_category_alternatives = self.alternatives_flows.loc[
                classified[classified['worse'] == alternative_row['worse']].index]
            better_category_alternatives = self.alternatives_flows.loc[
                classified[classified['worse'] == alternative_row['better']].index]

            alternative_net_outranking_flow = self.alternatives_flows[alternative]['positive'] \
                                              - self.alternatives_flows[alternative]['negative']

            worse_category_net_outranking_flow = worse_category_alternatives.apply(lambda row:
                                                                                   row['positive'] - row['negative'],
                                                                                   axis=1)

            better_category_net_outranking_flow = better_category_alternatives.apply(lambda row:
                                                                                     row['positive'] - row['negative'],
                                                                                     axis=1)

            positive_distance = worse_category_net_outranking_flow.map(lambda x:
                                                                       alternative_net_outranking_flow - x).sum()
            negative_distance = better_category_net_outranking_flow.map(lambda x:
                                                                        x - alternative_net_outranking_flow).sum()

            total_distance = 1 / worse_category_alternatives.shape[0] * positive_distance \
                             - 1 / better_category_alternatives.shape[0] * negative_distance

            if total_distance > self.cut_point:
                new_classification[alternative] = alternative_row['better']
            elif total_distance < self.cut_point:
                new_classification[alternative] = alternative_row['worse']
            else:
                if self.assign_to_better_class:
                    new_classification[alternative] = alternative_row['better']
                else:
                    new_classification[alternative] = alternative_row['worse']

        return new_classification

    def calculate_sorted_alternatives(self) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Sort alternatives to proper categories.

        :return: DataFrame with imprecise category assignments(worse and better class)
        and Series with precise assignments
        """
        first_step_assignments = self.__calculate_first_step_assignments()
        final_step_assignments = self.__calculate_final_assignments(first_step_assignments)

        return first_step_assignments, final_step_assignments
