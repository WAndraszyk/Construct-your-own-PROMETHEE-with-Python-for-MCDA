from ModularParts.flows.M9_PrometheeOutrankingFlows import PrometheeOutrankingFlows
from Example1Data import *
from M7_PrometheeVeto_TEST import overall_preference

positive_flows, negative_flows = PrometheeOutrankingFlows(alternatives, overall_preference).calculate_flows()

print("------------------------OUTRANKING FLOWS---------------")
print("Positive flows: \n", positive_flows)
print("Negative flows: \n", negative_flows)
