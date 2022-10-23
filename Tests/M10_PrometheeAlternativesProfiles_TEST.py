from ModularParts.preference.M3_PrometheePreference import PrometheePreference
from ModularParts.alternatives_profiles.M10_PrometheeAlternativesProfiles import PrometheeAlternativesProfiles
from DecisionProblemData import *

## M-3 Preferences
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

## M10 PrometheeAlternativesProfiles
M10_criteria = [(criterion_name, criterion_weight) for criterion_name, criterion_weight in
                zip(criteria, criteria_weights)]

prom_alt_pro = PrometheeAlternativesProfiles(alternatives=alternatives,
                                             criteria=M10_criteria,
                                             partial_preferences=partial_preferences)

alternatives_profiles = prom_alt_pro.calculate_alternatives_profiles()

for a in alternatives_profiles.items():
    print(a)


