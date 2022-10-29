import pytest
import sys
import pandas as pd
from pandas.testing import assert_series_equal
from core.enums import ScoringFunction, ScoringFunctionDirection
from core.enums import CompareProfiles
from modular_parts.sorting import calculate_flowsort_gdss_sorted_alternatives

sys.path.append('../..')


@pytest.fixture
def alternatives_general_net_flows():
    alternatives = [f"a{i}" for i in range(1, 47)]
    return pd.Series([-0.359, -0.354, -0.275, -0.238, -0.026, -0.227, -0.234, -0.025, -0.258,
                      -0.198, -0.195, -0.195, -0.196, 0.095, -0.156, -0.065, -0.158, -0.124,
                      -0.125, -0.023, -0.18, -0.148, -0.151, -0.119, -0.076, -0.012, -0.114,
                      0.022, -0.052, -0.057, -0.06, -0.053, 0.047, 0.088, 0.058, 0.21, 0.162,
                      0.16, 0.1, 0.135, 0.234, 0.13, 0.165, 0.179, 0.179, 0.321], index=alternatives)


@pytest.fixture
def profiles_general_net_flows():
    alternatives = [f"a{i}" for i in range(1, 47)]
    DMs = [f"DM{i}" for i in range(1, 4)]
    profiles = [f"p{i}" for i in range(1, 3)]
    DM1 = pd.DataFrame([
        [0.254, 0.253, 0.24, 0.234, 0.199, 0.232, 0.234, 0.198, 0.237, 0.227,
         0.226, 0.226, 0.227, 0.178, 0.22, 0.205, 0.22, 0.215, 0.215, 0.198,
         0.224, 0.218, 0.219, 0.214, 0.207, 0.196, 0.213, 0.191, 0.203, 0.204,
         0.204, 0.203, 0.186, 0.179, 0.184, 0.159, 0.167, 0.167, 0.177, 0.172,
         0.155, 0.172, 0.166, 0.164, 0.164, 0.141],
        [-0.109, -0.109, -0.123, -0.129, -0.164, -0.131, -0.128, -0.164, -0.125,
         -0.136, -0.136, -0.136, -0.136, -0.184, -0.142, -0.157, -0.142, -0.148,
         -0.147, -0.164, -0.138, -0.144, -0.143, -0.148, -0.156, -0.166, -0.149,
         -0.172, -0.16, -0.159, -0.159, -0.159, -0.176, -0.183, -0.178, -0.203,
         -0.195, -0.195, -0.185, -0.191, -0.207, -0.19, -0.196, -0.198, -0.198, -0.222]]
        , index=profiles, columns=alternatives)

    DM2 = pd.DataFrame([
        [0.218, 0.218, 0.204, 0.198, 0.163, 0.196, 0.199, 0.163, 0.201, 0.192,
         0.191, 0.191, 0.191, 0.143, 0.185, 0.17, 0.185, 0.179, 0.179, 0.163,
         0.189, 0.183, 0.184, 0.179, 0.171, 0.161, 0.178, 0.155, 0.167, 0.168,
         0.168, 0.167, 0.151, 0.144, 0.149, 0.124, 0.132, 0.132, 0.142, 0.136,
         0.12, 0.132, 0.131, 0.129, 0.129, 0.105],
        [-0.049, -0.05, -0.063, -0.069, -0.105, -0.072, -0.069, -0.105, -0.066,
         -0.076, -0.077, -0.077, -0.077, -0.125, -0.083, -0.098, -0.083, -0.089,
         -0.088, -0.105, -0.079, -0.085, -0.084, -0.089, -0.096, -0.107, -0.09,
         -0.113, -0.1, -0.1, -0.099, -0.1, -0.117, -0.124, -0.119, -0.144, -0.136,
         -0.136, -0.125, -0.131, -0.148, -0.131, -0.137, -0.139, -0.139, -0.162]],
        index=profiles, columns=alternatives)

    DM3 = pd.DataFrame([
        [0.151, 0.15, 0.137, 0.13, 0.095, 0.128, 0.131, 0.095, 0.133, 0.124, 0.123,
         0.123, 0.123, 0.075, 0.117, 0.102, 0.117, 0.112, 0.112, 0.095, 0.121, 0.115,
         0.116, 0.111, 0.103, 0.093, 0.11, 0.087, 0.099, 0.1, 0.1, 0.099, 0.083, 0.076,
         0.081, 0.056, 0.064, 0.064, 0.074, 0.068, 0.052, 0.069, 0.063, 0.061, 0.061, 0.037],
        [-0.106, -0.107, -0.12, -0.126, -0.162, -0.129, -0.126, -0.162, -0.123, -0.133, -0.134,
         -0.134, -0.134, -0.182, -0.14, -0.155, -0.14, -0.145, -0.145, -0.162, -0.136,
         -0.142, -0.141, -0.147, -0.153, -0.164, -0.147, -0.17, -0.158, -0.157, -0.156,
         -0.157, -0.174, -0.181, -0.176, -0.201, -0.193, -0.401, -0.183, -0.188, -0.205,
         -0.188, -0.193, -0.196, -0.196, -0.219]],
        index=profiles, columns=alternatives)

    return pd.concat([DM1, DM2, DM3], keys=DMs)


@pytest.fixture
def categories():
    return ["C1", "C2", "C3"]


@pytest.fixture
def criteria_directions():
    return [0, 0, 0]


@pytest.fixture
def profiles_performances():
    alternatives = [f"a{i}" for i in range(1, 47)]
    criteria = [f"g{i}" for i in range(1, 4)]
    return pd.DataFrame([[2, 2, 1],
                         [10, 2, 1],
                         [3, 4, 1],
                         [2, 4, 2],
                         [2, 2, 10],
                         [15, 5, 1],
                         [15, 2, 4],
                         [3, 2, 10],
                         [42, 3, 2],
                         [9, 4, 3],
                         [14, 4, 3],
                         [13, 4, 3],
                         [12, 4, 3],
                         [604, 4, 2],
                         [17, 4, 4],
                         [14, 8, 2],
                         [14, 4, 4],
                         [8, 4, 5],
                         [6, 4, 5],
                         [6, 2, 10],
                         [40, 4, 3],
                         [24, 5, 3],
                         [26, 4, 4],
                         [151, 4, 3],
                         [45, 2, 8],
                         [27, 2, 10],
                         [35, 3, 6],
                         [12, 3, 10],
                         [72, 4, 6],
                         [63, 4, 6],
                         [58, 4, 6],
                         [53, 6, 4],
                         [41, 8, 6],
                         [191, 4, 8],
                         [137, 4, 8],
                         [412, 4, 8],
                         [31, 7, 9],
                         [28, 7, 9],
                         [62, 6, 8],
                         [49, 7, 8],
                         [19, 8, 10],
                         [107, 7, 7],
                         [37, 7, 9],
                         [62, 7, 9],
                         [54, 8, 8],
                         [26, 10, 10]], index=alternatives, columns=criteria)


@pytest.fixture
def dms_weights():
    return pd.Series([1, 1, 1], index=["DM1", "DM2", "DM3"])


@pytest.fixture
def comparison_with_profiles():
    return CompareProfiles.LIMITING_PROFILES


@pytest.fixture
def assign_to_better_class():
    return True


def test_net_flow_score_sum_favor(alternatives_preferences):
    



if __name__ == '__main__':
    test_net_flow_score_sum_favor(alternatives_preferences)
    test_net_flow_score_min_against(alternatives_preferences)
    test_net_flow_score_max_difference(alternatives_preferences)
