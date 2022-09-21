from ModularParts.M7_PrometheeVeto import PrometheeVeto
from M3_PrometheePreference_TEST import preference
from Example1Data import *

veto, partial_veto = PrometheeVeto(criteria, alternatives_performances, weights,
                                   veto_thr, criteria_directions).compute_veto()

print("-------------VETO--------------")
for i in veto:
    print(i)

overall_preference = PrometheeVeto(criteria, alternatives_performances, weights,
                                   veto_thr, criteria_directions).compute_veto(preference)

print("----------OVERALL PREFERENCE-------------")
for i in overall_preference:
    print(i)
