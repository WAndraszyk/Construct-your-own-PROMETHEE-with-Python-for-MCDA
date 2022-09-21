from ModularParts.M3_PrometheePreference import PrometheePreference
from ModularParts.M24_OrderedClustering import OrderedClustering
from Tests.DecisionProblemData import *

# M-3 Preferences
pro_pref = PrometheePreference(alternatives=alternatives, criteria=criteria,
                               alternatives_performances=alternatives_performances,
                               weights=criteria_weights,
                               p_list=preference_thresholds,
                               q_list=indifference_thresholds,
                               s_list=standard_deviations,
                               generalized_criteria=generalized_criteria,
                               directions=criteria_directions,
                               decimal_place=3)

preferences, partial_preferences = pro_pref.computePreferenceIndices()

# M24 OrderedClustering
clusters = OrderedClustering(alternatives, preferences).group_alternatives(5)
for i in clusters:
    print(i)
