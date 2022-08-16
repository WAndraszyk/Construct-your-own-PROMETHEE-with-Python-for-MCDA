from core.aliases import NumericValue
from typing import List, Tuple, Dict
from core.preference_commons import directed_alternatives_performances


class PromSort:
    """
    This module computes the assignments of given alternatives to categories using PromSort.
    """

    def __init__(self,
                 alternatives: List[str],
                 categories: List[str],
                 category_profiles: List[str],
                 profiles_performances: List[List[NumericValue]],
                 criteria: Tuple[List[NumericValue], List[NumericValue]],
                 # in pdf: description, importance etc. in code: thresholds and preference directions (0 or 1)
                 negative_flows: Tuple[List[NumericValue], List[NumericValue]],
                 positive_flows: Tuple[List[NumericValue], List[NumericValue]],
                 cut_point: NumericValue,  # <-1, 1>, used in second phase
                 assign_to_better_class: bool = True):
        """
        :param alternatives: List of alternatives names (strings only)
        :param categories: List of categories names (strings only)
        :param category_profiles: List of boundary profiles names which divide alternatives
        to proper categories (strings only)
        :param profiles_performances: 2D List of performances of each boundary profile in each criterion
        :param criteria: List of threshold of each criterion
        and List of preference direction (0 for 'min' and 1 for 'max')
        :param negative_flows: List of negative flows of each alternative
        and List of negative flows of each boundary profile
        :param positive_flows: List of positive flows of each alternative
        and List of positive flows of each boundary profile
        :param cut_point: Numeric Value in range <-1, 1> which define DM preference of classifying alternative to worse
        or better class in final alternative assignment
        (-1 means 'always worse category', 1 means 'always better category')
        :param assign_to_better_class: Boolean which describe preference of the DM in final alternative assignment if
        total distance is equal cut_point value.
        """
        self.alternatives = alternatives
        self.categories = categories
        self.category_profiles = category_profiles
        self.profiles_performances = directed_alternatives_performances(profiles_performances, criteria[1])
        self.criteria = criteria
        self.negative_flows = negative_flows
        self.positive_flows = positive_flows
        self.cut_point = cut_point
        self.assign_to_better_class = assign_to_better_class
        self.__check_if_profiles_are_strictly_worse()

    def __check_if_profiles_are_strictly_worse(self):
        """
        Check if each boundary profile is strictly worse in each criterion by specified threshold than betters profiles

        :raise ValueError: if any profile is not strictly worse in any criterion than anny better profile
        """
        for criteria_i, threshold in enumerate(self.criteria[0]):
            for i, profile_i in enumerate(self.profiles_performances[:-1]):
                profile_j = self.profiles_performances[i + 1]
                if profile_i[criteria_i] + threshold > profile_j[criteria_i]:
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
        outranking_relations = []
        for profile_positive_flow, profile_negative_flow in zip(self.positive_flows[1], self.negative_flows[1]):
            outranking_relations.append(
                PromSort.__define_outranking_relation(profile_positive_flow, profile_negative_flow,
                                                      alternative_positive_flow, alternative_negative_flow))
        return set(outranking_relations) == {"P"}

    def __calculate_first_step_assignments(self) -> Tuple[Dict[str][List[str]],
                                                          List[Tuple[str, Tuple[str, str]]]]:
        """
        Calculates first step of assignments alternatives to categories.
        This function calculates outranking relations alternative to each boundary profile, then:
        - if alternative is preferred to all boundary profiles then assign alternative to the best category
        - calculate outranking relations of each boundary profile to alternative, if all boundary profiles are
        preferred to alternative then assign alternative to the worst category
        - if first incomparable or indifference appeared to the worse profile than first preference then assign
        alternative to first preference index + 1 category
        - else mark alternative as 'not_classified'. This alternative will be assigned to first incomparable
        or indifference index or first incomparable or indifference +1 category

        :return: Dictionary with classifications and List of Tuples of alternative, worse and better class to
        which can be alternative assigned in final assignments step
        """

        classification = {category: [] for category in self.categories}
        not_classified = []

        for alternative_name, alternative_positive_flow, alternative_negative_flow in zip(
                self.alternatives, self.positive_flows[0], self.negative_flows[0]):
            outranking_relations = []
            for profile_positive_flow, profile_negative_flow in zip(self.positive_flows[1], self.negative_flows[1]):
                outranking_relations.append(
                    PromSort.__define_outranking_relation(alternative_positive_flow, alternative_negative_flow,
                                                          profile_positive_flow, profile_negative_flow))

            first_P_occurrence = outranking_relations.index("P") if "P" in outranking_relations else float("inf")
            first_R_occurrence = outranking_relations.index("?") if "?" in outranking_relations else float("inf")
            first_I_occurrence = outranking_relations.index("I") if "I" in outranking_relations else float("inf")

            if outranking_relations[-1] == "P":
                classification[self.categories[-1]].append(alternative_name)
            elif self.__check_if_all_profiles_are_preferred_to_alternative(
                    alternative_positive_flow, alternative_negative_flow):
                classification[self.categories[0]].append(alternative_name)
            elif min(first_R_occurrence, first_I_occurrence) < first_P_occurrence:
                classification[self.categories[first_P_occurrence + 1]].append(alternative_name)
            else:
                s = min(first_R_occurrence, first_I_occurrence)
                not_classified.append((alternative_name, (self.categories[s], self.categories[s + 1])))

        return classification, not_classified

    def __calculate_final_assignments(self, classification: Dict[str][List[str]],
                                      not_classified: List[Tuple[str, Tuple[str, str]]]) -> Dict[str][List[str]]:
        """
        Used assigned categories to assign the unassigned ones. Based on positive and negative distance,
        that is calculated for each alternative, basing on calculated in first step categories (s and s+1).
        After calculating positive and negative distances a total distance is determining.
        After computing the total distance for all alternatives and profiles it is compared with cut point parameter.

        :param classification: Dictionary with classifications from first step assignments
        :param not_classified: List of Tuples of alternative, worse and better class to
        which can be alternative assigned in this step.

        :return: Dictionary with final alternatives classification
        """

        new_classification = classification

        for alternative, worse_category, better_category in not_classified:
            alternative_index = self.alternatives.index(alternative)
            worse_category_alternatives = classification[worse_category]
            better_category_alternatives = classification[better_category]
            worse_category_alternatives_indices = \
                [self.alternatives.index(alternative_i) for alternative_i in worse_category_alternatives]
            better_category_alternatives_indices = \
                [self.alternatives.index(alternative_i) for alternative_i in better_category_alternatives]

            alternative_net_outranking_flow = \
                self.positive_flows[0][alternative_index] - self.negative_flows[0][alternative_index]
            worse_category_alternatives_net_outranking_flows = \
                [self.positive_flows[0][alternative_index_i] - self.negative_flows[0][alternative_index_i]
                 for alternative_index_i in worse_category_alternatives_indices]
            better_category_alternatives_net_outranking_flows = \
                [self.positive_flows[0][alternative_index_i] - self.negative_flows[0][alternative_index_i]
                 for alternative_index_i in better_category_alternatives_indices]

            positive_distance = \
                sum([alternative_net_outranking_flow - worse_category_alternative_net_outranking_flow
                     for worse_category_alternative_net_outranking_flow
                     in worse_category_alternatives_net_outranking_flows])

            negative_distance = \
                sum([better_category_alternative_net_outranking_flow - alternative_net_outranking_flow
                     for better_category_alternative_net_outranking_flow
                     in better_category_alternatives_net_outranking_flows])

            total_distance = 1 / len(worse_category_alternatives) * positive_distance \
                             - 1 / len(better_category_alternatives) * negative_distance

            if total_distance > self.cut_point:
                new_classification[better_category].append(alternative)
            elif total_distance < self.cut_point:
                new_classification[worse_category].append(alternative)
            else:
                if self.assign_to_better_class:
                    new_classification[better_category].append(alternative)
                else:
                    new_classification[worse_category].append(alternative)

        return new_classification

    def calculate_sorted_alternatives(self) -> Tuple[Dict[str][List[str]], Dict[str][List[str]]]:
        """
        Sort alternatives to proper categories.

        :return: Dictionary with final alternatives classification
        and Dictionary with classifications from first step assignments.
        """
        first_step_assignments, not_classified = self.__calculate_first_step_assignments()
        final_step_assignments = self.__calculate_final_assignments(first_step_assignments, not_classified)

        return first_step_assignments, final_step_assignments
