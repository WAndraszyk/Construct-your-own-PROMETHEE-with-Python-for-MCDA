class PrometheePreference:
    def __init__(self, alternatives, criteria, alternatives_performances, weights, generalized_criterion="usual",
                 decimal_place=3):
        """
        Nie uwzględniono boundary profiles oraz characteristic profiles.
        :param alternatives: list of alternatives (rozumiemy to jako liste samych nazw)
        :param criteria: list of criteria
        :param alternatives_performances: 2D list of alternatives' value at every criterion
        :param weights: list of weights
        :param generalized_criterion: method used for computing partial preference indices
        :param decimal_place:
        """
        self.alternatives = alternatives
        self.criteria = criteria
        self.alternatives_performances = alternatives_performances
        self.weights = weights
        self.decimal_place = decimal_place
        self.generalized_criterion = generalized_criterion

        ### GENERALIZED_CRITERIONS

    def __usualCriterion(self, d):
        if d <= 0:
            return 0
        else:
            return 1

    def __uShapeCriterion(self, d, q):
        if d <= q:
            return 0
        else:
            return 1

    def __vShapeCriterion(self, d, p):
        if d <= 0:
            return 0
        elif d <= p:
            return round(d / p, self.decimal_place)
        else:
            return 1

    def __levelCriterion(self, d, p, q):
        if d <= q:
            return 0
        elif d <= p:
            return 0.5
        else:
            return 1

    def __vShapeIndifferenceCriterion(self, d, p, q):
        if d <= q:
            return 0
        elif d <= p:
            return round((d - q) / (p - q), self.decimal_place)
        else:
            return 1

    def __gaussianCriterion(self, d, s):
        e = 2.718281828459045
        if d <= 0:
            return 0
        else:
            return 1 - e ** (-((d ** 2) / (2 * s ** 2)))

    def __deviations(self):
        deviations = []
        for k in range(len(self.criteria)):
            comparisons = []
            for i in range(len(self.alternatives_performances)):
                comparison_direct = []
                for j in range(len(self.alternatives_performances)):
                    comparison_direct.append(
                        self.alternatives_performances[i][k] - self.alternatives_performances[j][k])
                comparisons.append(comparison_direct)
            deviations.append(comparisons)
        return deviations

    def __partialPreference(self, method, q=0.25, p=0.75, s=0.5, ):
        deviations = self.__deviations()
        ppIndices = []
        for k in range(len(self.criteria)):
            criterionIndices = []
            for i in range(len(self.alternatives_performances)):
                alternativeIndices = []
                for j in range(len(self.alternatives_performances)):
                    alternativeIndices.append(method(deviations[k][i][j]))  # q,p,s?
                criterionIndices.append(alternativeIndices)
            ppIndices.append(criterionIndices)
        return ppIndices

    def computePreferenceIndices(self):
        """
        Wstępnie zaimplementowana metoda która sztywno uzywa usualCriterion, docelowo metoda na podstawie zmiennej generalised criterion (param2).
        :return: OUT1, OUT2
        """
        partialPref = self.__partialPreference(self.__usualCriterion)
        aggregatedPI = []
        for i in range(len(self.alternatives_performances)):
            for j in range(len(self.alternatives_performances)):
                Pi_A_B = 0
                for k in range(len(self.criteria)):
                    Pi_A_B += partialPref[k][i][j] * self.weights[k]
                aggregatedPI.append(Pi_A_B)
        return aggregatedPI, partialPref
