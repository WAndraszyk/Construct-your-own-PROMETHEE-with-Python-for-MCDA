from ModularParts.weights.M1_SurrogateWeights import SurrogateWeights
from ModularParts.preference.M3_PrometheePreference import PrometheePreference
from ModularParts.preference.M7_PrometheeVeto import PrometheeVeto
from Tests.DecisionProblemData import *

alternatives_performances = pd.DataFrame(data=alternatives_performances, index=alternatives, columns=criteria)
preference_thresholds = pd.Series(data=preference_thresholds, index=criteria)
indifference_thresholds = pd.Series(data=indifference_thresholds, index=criteria)
standard_deviations = pd.Series(data=standard_deviations, index=criteria)
generalized_criteria = pd.Series(data=generalized_criteria, index=criteria)
criteria_directions = pd.Series(data=criteria_directions, index=criteria)
veto_thresholds = pd.Series(data= veto_thr, index=criteria)
weights = SurrogateWeights(ranked_criteria=pd.Series(data=[7, 1, 3, 2, 4, 5, 6], index=criteria)).rank_sum()
preference, partial_preference = PrometheePreference(alternatives_performances, preference_thresholds,
                                                     indifference_thresholds, standard_deviations, generalized_criteria,
                                                     criteria_directions, weights).computePreferenceIndices()


veto, partial_veto = PrometheeVeto(alternatives_performances = alternatives_performances, weights=weights,
                                   v_list =veto_thresholds, directions= criteria_directions).compute_veto()

print(partial_veto)