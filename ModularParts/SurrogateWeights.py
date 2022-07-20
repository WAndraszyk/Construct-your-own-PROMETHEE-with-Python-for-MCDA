from core.aliases import NumericValue
from typing import List


class SurrogateWeights:
    """This class computes weights of criteria. It requires the user to specify the
    criteria ranking. In this ranking each criterion is associated with a unique position.
    The ranking should list the criteria from the most to least important."""

    def __init__(self, criteria_rank,
                 criteria: List[str],
                 decimal_place: NumericValue = 3):
        self.criteria = criteria
        self.decimal_place = decimal_place
        self.criteria_rank = criteria_rank

    def __weightOrder(self,
                      weights: List[NumericValue]) -> List[NumericValue]:
        weightsOut = []
        for num_a, crit in enumerate(self.criteria):
            for num_b, critOrderd in enumerate(self.criteria_rank):
                if crit == critOrderd:
                    weightsOut.append(weights[num_b])
                    break
        return weightsOut

    def equalWeights(self) -> List[NumericValue]:
        """
        In this method all weights are computed with the same value and sum up to 1.

        :return: List of weights of the criteria.
        """
        n = len(self.criteria_rank)
        weights = []
        wi = round(1 / n, self.decimal_place)
        for i in range(1, n + 1):
            weights.append(wi)
        weightsOrdered = self.__weightOrder(weights)
        return weightsOrdered

    def rankSum(self) -> List[NumericValue]:
        """
        In this method the more important the criterion is, the higher its weight.

        :return: List of weights of the criteria.
        """
        n = len(self.criteria_rank)
        weights = []
        for i in range(1, n + 1):
            weights.append(round(2 * (n + 1 - i) / (n * (n + 1)), self.decimal_place))
        weightsOrdered = self.__weightOrder(weights)
        return weightsOrdered

    def reciprocalOfRanks(self) -> List[NumericValue]:
        """
        This method computes weights by dividing each reciprocal of rank by the sum of these
        reciprocals for all criteria.

        :return: List of weights of the criteria.
        """
        n = len(self.criteria_rank)
        weights = []
        sigma = 0
        for j in range(1, n + 1):
            sigma += 1 / j
        for i in range(1, n + 1):
            weights.append(round((1 / i) / sigma, self.decimal_place))
        weightsOrdered = self.__weightOrder(weights)
        return weightsOrdered

    def rankOrderCentroid(self) -> List[NumericValue]:
        """
        The weights in this method reflect the centroid of the simplex defined by ranking of
        the criteria.

        :return: List of weights of the criteria.
        """
        n = len(self.criteria_rank)
        weights = []
        sigma = 0
        for j in range(1, n + 1):
            sigma += 1 / j
        wi = round((1 / n) * sigma, self.decimal_place)
        for i in range(1, n + 1):
            weights.append(wi)
        weightsOrdered = self.__weightOrder(weights)
        return weightsOrdered
