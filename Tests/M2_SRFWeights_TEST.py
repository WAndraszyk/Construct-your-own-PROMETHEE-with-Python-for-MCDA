from ModularParts.M2_SRFWeights import SRFWeights

criteria = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']
criteria_ranks = [6, 4, 1, 2, 5, 4, 1, 6, 4, 4, 7, 1]
criteria_weight_ratio = 6.5

srf = SRFWeights(criteria, criteria_ranks, criteria_weight_ratio, decimal_place=1)

x = srf.calculate_srf_weights()
print(x, sum(x))
# e = 11 (not 12)
# g = 3 (not 2)
# k = 14 (not 15)
# l = 3 (not 2)

