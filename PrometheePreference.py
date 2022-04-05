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
        :param decimal_place: with this you can choose the decimal_place of the output numbers
        """
        self.alternatives = alternatives
        self.criteria = criteria
        self.alternatives_performances = alternatives_performances
        self.weights = weights
        self.decimal_place = decimal_place
        self.generalized_criterion = '_PrometheePreference__' + generalized_criterion + 'Criterion'

        # GENERALIZED_CRITERIONS:

    def __usualCriterion(self, d):
        """
        Returns 0 if difference is less or equal to 0, if not it returns 1.

        :param d: difference between two alternatives on a specified criterion
        """
        if d <= 0:
            return 0
        else:
            return 1

    def __uShapeCriterion(self, d, q):
        """
        Returns 0 if difference is less or equal to q, if not it returns 1.

        :param d: difference between two alternatives on a specified criterion
        :param q: threshold of indifference
        """
        if d <= q:
            return 0
        else:
            return 1

    def __vShapeCriterion(self, d, p):
        """
        Returns 0 if difference is less or equal to p, 1 if it is greater then p.
        Else it calculates the number between 0 and 1 based on the difference.

        :param d: difference between two alternatives on a specified criterion
        :param p: threshold of strict prefference
        """
        if d <= 0:
            return 0
        elif d <= p:
            return round(d / p, self.decimal_place)
        else:
            return 1

    def __levelCriterion(self, d, p, q):
        """
        Returns: 0 for d<=q
                 0.5 for q<d<=p
                 1 for d>p

        :param d: difference between two alternatives on a specified criterion
        :param p: threshold of strict prefference
        :param q: threshold of indifference
        """
        if d <= q:
            return 0
        elif d <= p:
            return 0.5
        else:
            return 1

    def __vShapeIndifferenceCriterion(self, d, p, q):
        """
        Returns 0 if difference is less or equal to q, 1 if it is greater then p.
        Else it calculates the number between 0 and 1 based on the difference.

        :param d: difference between two alternatives on a specified criterion
        :param p: threshold of strict prefference
        :param q: threshold of indifference
        """
        if d <= q:
            return 0
        elif d <= p:
            return round((d - q) / (p - q), self.decimal_place)
        else:
            return 1

    def __gaussianCriterion(self, d, s):
        """
        Calculates preference based on nonlinear gaussian function.

        :param s: intermediate value between q and p. Defines the inflection point of the preference function.
        :param d: difference between two alternatives on a specified criterion
        """
        e = 2.718281828459045
        if d <= 0:
            return 0
        else:
            return 1 - e ** (-((d ** 2) / (2 * s ** 2)))

    def __deviations(self):
        """
        Compares alternatives on criteria.

        :return: 3D matrix of deviations in evaluations on criteria
        """
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
        """
        Calculates partial preference of every alternative over others at every criterion
        based on deviations using a method chosen by user.

        :param method: method used for computing partial preference indices
        :param q: threshold of indifference
        :param p: threshold of strict prefference
        :param s: intermediate value between q and p. Defines the inflection point of the preference function.
        :return: partial preference indices
        """
        deviations = self.__deviations()
        ppIndices = []
        for k in range(len(self.criteria)):
            criterionIndices = []
            for i in range(len(self.alternatives_performances)):
                alternativeIndices = []
                for j in range(len(self.alternatives_performances)):
                    alternativeIndices.append(method(self, deviations[k][i][j]))  # q,p,s?
                criterionIndices.append(alternativeIndices)
            ppIndices.append(criterionIndices)
        return ppIndices

    def computePreferenceIndices(self):
        """
        Calculates preference of every alternative over others based on partial preferences

        :return: preferences
        :return: partial preferences
        """
        partialPref = self.__partialPreference(getattr(PrometheePreference, self.generalized_criterion))
        preferences =[]
        for i in range(len(self.alternatives_performances)):
            aggregatedPI = []
            for j in range(len(self.alternatives_performances)):
                Pi_A_B = 0
                for k in range(len(self.criteria)):
                    Pi_A_B += partialPref[k][i][j] * self.weights[k]
                aggregatedPI.append(Pi_A_B)
            preferences.append(aggregatedPI)

        return preferences, partialPref

