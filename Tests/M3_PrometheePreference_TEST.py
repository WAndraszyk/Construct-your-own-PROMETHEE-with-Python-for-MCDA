from ModularParts.preference.M3_PrometheePreference import PrometheePreference
from Example1Data import *

preference, partial_preference = PrometheePreference(alternatives, criteria, alternatives_performances, weights,
                                                     preference_thr, indifference_thr, sigma_thr, generalized_criterion,
                                                     criteria_directions).computePreferenceIndices()

print("----------------------PREFERENCE--------------")
for i in preference:
    print(i)
