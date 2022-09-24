from ModularParts.M5_PrometheePreferenceWithInteractions import PrometheePreferenceWithInteractions
from ModularParts.M24_OrderedClustering import OrderedClustering
from Tests.DecisionProblemData import *

# M5 Preferences
pro_pref = PrometheePreferenceWithInteractions(alternatives=alternatives, criteria=criteria,
                                               alternatives_performances=alternatives_performances,
                                               weights=criteria_weights,
                                               p_list=preference_thresholds,
                                               q_list=indifference_thresholds,
                                               s_list=standard_deviations,
                                               generalized_criteria=generalized_criteria,
                                               directions=criteria_directions,
                                               decimal_place=3,
                                               interactions=interactions)

preferences, partial_preferences = pro_pref.computePreferenceIndices()

for i in preferences:
    print(i)

# M24 OrderedClustering
clusters = OrderedClustering(alternatives, preferences).group_alternatives(5)
for i in clusters:
    print(i)
