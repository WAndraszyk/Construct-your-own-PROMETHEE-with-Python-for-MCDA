import pandas as pd
from core.aliases import NumericValue
from typing import List, Tuple, Dict


class GroupClassAcceptabilities:
    """
    This module calculates alternatives support (basic and unimodal).
    """

    def __init__(self,
                 categories: List[str],
                 assignments: List[pd.DataFrame]):
        """
        :param categories: List of categories names (strings only)
        :param assignments: List of imprecise alternatives assignments of each DM
        """
        self.categories = categories
        self.assignments = assignments
        self.alternatives = list(assignments[0].index)

    def __calculate_votes(self) -> pd.DataFrame:
        """
        Calculate how many votes are for putting each alternative in each category.

        :return: DataFrame with votes for each category for each alternative (index: alternatives, columns: categories)
        """
        votes = pd.DataFrame([[0 for __ in self.categories] for _ in self.alternatives], index=self.alternatives,
                             columns=self.categories)
        for DM_i, DM_assignments in enumerate(self.assignments):
            for alternative, alternative_row in DM_assignments.iterrows():
                if alternative_row['worse'] == alternative_row['better']:
                    votes.loc[alternative, alternative_row['worse']] += 1
                else:
                    votes.loc[alternative, alternative_row['worse']:alternative_row['better']] += 1

        return votes

    def __calculate_alternatives_support(self, votes: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates alternatives support for each alternative and category (percentage).

        :param votes: DataFrame with votes for each category
         for each alternative (index: alternatives, columns: categories)

        :return: DataFrame with alternative support for each category
         for each alternative (index: alternatives, columns: categories)
        """
        n_DM = len(self.assignments)
        alternatives_support = votes/n_DM * 100

        return alternatives_support

    def __calculate_unimodal_alternatives_support(self, alternatives_support: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates unimodal alternatives support for each alternative and category (percentage).

        :param alternatives_support: 2D List with alternative support for each category for each alternative

        :return: 2D List with unimodal alternative support for each category for each alternative
        """
        def unimodal_single_row(row: pd.Series) -> pd.Series:
            row_len = len(row)
            unimodal_row = pd.Series([0 for _ in range(row_len)], index=row.index)

            for i, (category, support) in enumerate(row.items()):
                if i == 0 or i == row_len - 1:
                    unimodal_row[category] = support
                else:
                    unimodal_row[category] = max(support, min(max(row.iloc[:i]), max(row.iloc[i+1:])))
            return unimodal_row

        unimodal_alternatives_support = alternatives_support.apply(unimodal_single_row, axis=1)

        return unimodal_alternatives_support

    def calculate_alternatives_support(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Transforms DM assignments, count votes and basing on them calculates alternatives support and
         unimodal alternatives support

        :return: Tuple with DataFrames as alternatives support and unimodal alternatives support
        """
        votes = self.__calculate_votes()
        alternatives_support = self.__calculate_alternatives_support(votes)
        unimodal_alternatives_support = self.__calculate_unimodal_alternatives_support(alternatives_support)

        return alternatives_support, unimodal_alternatives_support
