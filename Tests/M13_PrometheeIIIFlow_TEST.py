from ModularParts.M13_PrometheeIIIFlow import PrometheeIIIFlow
from M9_PrometheeOutrankingFlows_TEST import *
from M7_PrometheeVeto_TEST import overall_preference

intervals, pairs = PrometheeIIIFlow(alternatives, positive_flows, negative_flows,
                                    overall_preference).calculate_ranking(0.005)

print("--------------------PROMETHEEIII-------------")
for i in pairs:
    print(i)
