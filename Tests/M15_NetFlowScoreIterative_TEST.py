from ModularParts.preference.M3_PrometheePreference import PrometheePreference
from ModularParts.ranking.M15_NetFlowScoreIterative import NetFlowScoreIterative
from core.enums import ScoringFunction, ScoringFunctionDirection
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

## M15 NetFlowScoreIterative

netflowscore = NetFlowScoreIterative(alternatives=alternatives,
                                     preferences=preferences,
                                     function=ScoringFunction.SUM,
                                     direction=ScoringFunctionDirection.AGAINST)

alternatives_ranking = netflowscore.create_ranking()

print(alternatives_ranking)