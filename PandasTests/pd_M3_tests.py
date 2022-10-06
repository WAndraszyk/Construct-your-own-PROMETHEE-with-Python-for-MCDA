from PandasModularParts.pd_M1_SurrogateWeights import SurrogateWeights
from PandasModularParts.pd_M3_PrometheePreference import PrometheePreference
from PandasModularParts.pd_M6_PrometheeDiscordance import PrometheeDiscordance
from Tests.DecisionProblemData import *

alternatives_performances = pd.DataFrame(data=alternatives_performances, index=alternatives, columns=criteria)
preference_thresholds = pd.Series(data=preference_thresholds, index=criteria)
indifference_thresholds = pd.Series(data=indifference_thresholds, index=criteria)
standard_deviations = pd.Series(data=standard_deviations, index=criteria)
generalized_criteria = pd.Series(data=generalized_criteria, index=criteria)
criteria_directions = pd.Series(data=criteria_directions, index=criteria)
weights = SurrogateWeights(ranked_criteria=pd.Series(data=[7, 1, 3, 2, 4, 5, 6], index=criteria)).rank_sum()

preference, partial_preference = PrometheePreference(alternatives_performances, preference_thresholds,
                                                     indifference_thresholds, standard_deviations, generalized_criteria,
                                                     criteria_directions, weights).computePreferenceIndices()

print("----------------------PREFERENCE--------------")
print(partial_preference)
print(preference)

discordance, partial_discordance = PrometheeDiscordance(criteria, partial_preference).compute_discordance(3)
print(discordance)
