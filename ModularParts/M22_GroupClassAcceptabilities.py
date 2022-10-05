from core.aliases import NumericValue
from typing import List, Tuple, Dict


class GroupClassAcceptabilities:
    """
    This module calculates alternatives support (basic and unimodal).
    """

    def __init__(self,
                 alternatives: List[str],
                 categories: List[str],
                 assignments: List[Dict[str, List[str]]]):
        """
        :param alternatives: List of alternatives names (strings only)
        :param categories: List of categories names (strings only)
        :param assignments: List of imprecise alternatives assignments of each DM
        """
        self.alternatives = alternatives
        self.categories = categories
        self.assignments = assignments

    def __transform_assignments_to_upper_lower_bound_form(self) -> List[Dict[str, List[str]]]:
        """
        Transform assignments input to more preferable form in this method.

        :return: List of Dictionaries for each DM with lower and upper bound for each alternative
        """
        alternatives_bounds = []

        for DM_i, DM_assignments in enumerate(self.assignments):
            dm_alternatives_bounds = {alternative: [] for alternative in self.alternatives}
            for category_i, to_category_assignments in enumerate(DM_assignments.values()):
                for alternative in to_category_assignments:
                    dm_alternatives_bounds[alternative].append(self.categories[category_i])
            for (alternative, alternative_assignments) in dm_alternatives_bounds.items():
                if len(alternative_assignments) == 1:
                    dm_alternatives_bounds[alternative].append(alternative_assignments[0])
            alternatives_bounds.append(dm_alternatives_bounds)

        return alternatives_bounds

    def __calculate_votes(self, alternatives_bounds: List[Dict[str, List[str]]]) -> List[List[NumericValue]]:
        """
        Calculate how many votes are for putting each alternative in each category.

        :param alternatives_bounds: List of Dictionaries for each DM with lower and upper bound for each alternative

        :return: 2D List with votes for each category for each alternative
        """
        votes = [[0 for __ in self.categories] for _ in self.alternatives]
        for DM_i, DM_alternative_bounds in enumerate(alternatives_bounds):
            for alternative_i, alternative_bounds in enumerate(DM_alternative_bounds.values()):
                if alternative_bounds[0] == alternative_bounds[1]:
                    votes[alternative_i][self.categories.index(alternative_bounds[0])] += 1
                else:
                    for category in alternative_bounds:
                        votes[alternative_i][self.categories.index(category)] += 1

        return votes

    def __calculate_alternatives_support(self, votes: List[List[NumericValue]]) -> List[List[NumericValue]]:
        """
        Calculates alternatives support for each alternative and category (percentage).

        :param votes: 2D List with votes for each category for each alternative

        :return: 2D List with alternative support for each category for each alternative
        """
        n_dm = len(self.assignments)

        alternatives_support = [[category_alternative_votes / n_dm * 100 for category_alternative_votes
                                 in alternative_votes] for alternative_votes in votes]
        return alternatives_support

    def __calculate_unimodal_alternatives_support(self, alternatives_support: List[List[NumericValue]]
                                                  ) -> List[List[NumericValue]]:
        """
        Calculates unimodal alternatives support for each alternative and category (percentage).

        :param alternatives_support: 2D List with alternative support for each category for each alternative

        :return: 2D List with unimodal alternative support for each category for each alternative
        """
        n_categories = len(self.categories)
        unimodal_alternatives_support = []

        for alternative_supports in alternatives_support:
            unimodal_alternative_supports = []
            for category_i, category_alternative_support in enumerate(alternative_supports):
                if category_i == 0 or category_i == n_categories - 1:
                    unimodal_alternative_supports.append(category_alternative_support)
                else:
                    unimodal_alternative_supports.append(max(category_alternative_support,
                                                             min(max(alternative_supports[:category_i]),
                                                                 max(alternative_supports[category_i + 1:]))))
            unimodal_alternatives_support.append(unimodal_alternative_supports)

        return unimodal_alternatives_support

    def calculate_alternatives_support(self) -> Tuple[List[List[NumericValue]], List[List[NumericValue]]]:
        """
        Transforms DM assignments, count votes and basing on them calculates alternatives support and
         unimodal alternatives support

        :return: Tuple with alternatives support and unimodal alternatives support
        """
        alternatives_bounds = self.__transform_assignments_to_upper_lower_bound_form()
        votes = self.__calculate_votes(alternatives_bounds)
        alternatives_support = self.__calculate_alternatives_support(votes)
        unimodal_alternatives_support = self.__calculate_unimodal_alternatives_support(alternatives_support)

        return alternatives_support, unimodal_alternatives_support
