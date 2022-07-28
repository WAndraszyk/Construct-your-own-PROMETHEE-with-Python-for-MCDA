import numpy as np
from core.aliases import NumericValue
from typing import List, Union
from core.net_flow_score import ScoringFunction, ScoringFunctionDirection


#  NOTATKI:
#  Bez category_profiles?


class NetFlowScore:
    """
    This class computes Net Flow Score which bases on calculating scores associated with
    each alternative.
    """

    def __init__(self, preferences: List[List[NumericValue]], function: ScoringFunction,
                 direction: ScoringFunctionDirection):
        """
        :param preferences: 2D List of aggregated preferences between each alternative.
        :param function: Enum ScoringFunction - indicate which function should be used in calculating Net Flow Score.
        :param direction: Enum ScoringFunctionDirection - indicate which function direction should be used in
                          calculating Net Flow Score.
        """
        self.preferences = np.ndarray(preferences)
        np.fill_diagonal(self.preferences, np.NaN)
        self.function = function
        self.direction = direction

    def __calculate_score(self, preferences: np.ndarray) -> np.ndarray:
        """
        Calculates scores for passed preferences.

        :param preferences: 2D List of aggregated preferences between alternatives.
        :return: List of Net Flow Scores for passed preferences.
        """

        if self.function is ScoringFunction.MAX:
            function = np.nanmax
        elif self.function is ScoringFunction.MIN:
            function = np.nanmin
        elif self.function is ScoringFunction.SUM:
            function = np.nansum
        else:
            raise ValueError(f"Incorrect scoring function: {self.function}")

        if self.direction is ScoringFunctionDirection.IN_FAVOR:
            scores = function(preferences, axis=1)
        elif self.direction is ScoringFunctionDirection.AGAINST:
            scores = -function(preferences, axis=0)
        elif self.direction is ScoringFunctionDirection.DIFFERENCE:
            scores = function(preferences - preferences.T, axis=1)
        else:
            raise ValueError(f"Incorrect scoring function direction: {self.direction}")

        return scores

    @staticmethod
    def __find_duplicates_values(array: Union[List, np.ndarray]) -> set:
        seen = set()
        duplicated_values = set()

        for x in array:
            if x in seen:
                duplicated_values.add(x)
            else:
                seen.add(x)

        return duplicated_values

    def calculate_net_flows_score(self, avoid_same_scores: bool = False) -> np.ndarray:
        """
        Calculates scores for all preferences.

        :param avoid_same_scores: If True and calculate_scores returns some equal scores calculate once more scores for
                                  alternatives which get the same score.
        :return: List of Net Flow Scores for all preferences.
        """
        if avoid_same_scores:
            scores = self.__calculate_score(self.preferences)
            if len(scores) != len(set(scores)):
                duplicated_values = self.__find_duplicates_values(scores)
                for duplicated_value in duplicated_values:
                    duplicated_score_indices = [i for i, score in enumerate(scores) if score == duplicated_value]
                    sub_preferences = self.preferences[:, duplicated_score_indices][duplicated_score_indices, :]
                    sub_scores = self.__calculate_score(sub_preferences)
                    for index, score in zip(duplicated_score_indices, sub_scores):
                        scores[index] = score
        else:
            scores = self.__calculate_score(self.preferences)

        return scores
