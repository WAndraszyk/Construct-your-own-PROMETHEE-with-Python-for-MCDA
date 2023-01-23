import pandas as pd
import pytest
from pandas.testing import assert_frame_equal, assert_series_equal

from modular_parts.M12_GDSSNetFlows import calculate_gdss_flows


@pytest.fixture
def dms_partial_preferences():
    alternatives = [f"a{i}" for i in range(1, 13)]
    profiles = [f"p{i}" for i in range(1, 4)]
    criteria = [f"g{i}" for i in range(1, 6)]

    DM1_g1_profiles_partial_preferences = pd.DataFrame(
        [
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.8, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.5, 0.0],
            [0.6, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0, 0.4, 0.0, 1.0, 1.0, 0.0],
        ],
        index=profiles,
        columns=alternatives,
    )

    DM1_g2_profiles_partial_preferences = pd.DataFrame(
        [
            [0.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0],
            [0.0, 0.2, 0.0, 1.0, 0.0, 0.0, 0.5, 0.0, 0.0, 1.0, 0.0, 0.0],
            [0.7, 1.0, 0.8, 1.0, 0.0, 0.5, 1.0, 0.0, 0.5, 1.0, 0.5, 0.0],
        ],
        index=profiles,
        columns=alternatives,
    )

    DM1_g3_profiles_partial_preferences = pd.DataFrame(
        [
            [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.714285714285714,
                0.0,
                0.0,
                0.714285714285714,
                0.0,
                0.714285714285714,
                0.0,
            ],
            [
                0.0,
                0.0,
                0.0,
                0.285714285714286,
                0.0,
                1.0,
                0.0,
                0.0,
                1.0,
                1.0,
                1.0,
                0.0,
            ],
            [
                0.571428571428571,
                0.0,
                0.0,
                1.0,
                1.0,
                1.0,
                1.0,
                0.285714285714286,
                1.0,
                1.0,
                1.0,
                0.0,
            ],
        ],
        index=profiles,
        columns=alternatives,
    )

    DM1_g4_profiles_partial_preferences = pd.DataFrame(
        [
            [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.999999999977103,
                0.0,
                0.0,
                0.393469340287367,
                0.988891003461758,
                0.999999999977103,
                0.0,
            ],
            [0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0],
        ],
        index=profiles,
        columns=alternatives,
    )

    DM1_g5_profiles_partial_preferences = pd.DataFrame(
        [
            [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.166666666666667,
                0.0,
                0.0,
            ],
            [
                0.0,
                0.166666666666667,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,
                1.0,
                0.0,
            ],
            [
                0.166666666666667,
                1.0,
                1.0,
                1.0,
                0.0,
                0.166666666666667,
                1.0,
                0.166666666666667,
                0.0,
                1.0,
                1.0,
                0.0,
            ],
        ],
        index=profiles,
        columns=alternatives,
    )

    DM1_profiles_partial_preferences = pd.concat(
        [
            DM1_g1_profiles_partial_preferences,
            DM1_g2_profiles_partial_preferences,
            DM1_g3_profiles_partial_preferences,
            DM1_g4_profiles_partial_preferences,
            DM1_g5_profiles_partial_preferences,
        ],
        keys=criteria,
    )

    DM1_g1_alternatives_partial_preferences = pd.DataFrame(
        [
            [1.0, 0.4, 0.0],
            [0.7, 0.0, 0.0],
            [0.5, 0.0, 0.0],
            [0.5, 0.0, 0.0],
            [0.5, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 0.6, 0.0],
            [1.0, 1.0, 0.2],
            [0.5, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.2],
        ],
        index=alternatives,
        columns=profiles,
    )

    DM1_g2_alternatives_partial_preferences = pd.DataFrame(
        [
            [1.0, 0.3, 0.0],
            [0.8, 0.0, 0.0],
            [1.0, 0.2, 0.0],
            [0.0, 0.0, 0.0],
            [1.0, 1.0, 0.5],
            [1.0, 0.5, 0.0],
            [0.5, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [1.0, 0.5, 0.0],
            [0.0, 0.0, 0.0],
            [1.0, 0.5, 0.0],
            [1.0, 1.0, 0.0],
        ],
        index=alternatives,
        columns=profiles,
    )

    DM1_g3_alternatives_partial_preferences = pd.DataFrame(
        [
            [1.0, 0.857142857142857, 0.0],
            [1.0, 1.0, 0.142857142857143],
            [1.0, 1.0, 0.142857142857143],
            [0.714285714285714, 0.0, 0.0],
            [1.0, 0.428571428571429, 0.0],
            [0.0, 0.0, 0.0],
            [1.0, 0.428571428571429, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
        ],
        index=alternatives,
        columns=profiles,
    )

    DM1_g4_alternatives_partial_preferences = pd.DataFrame(
        [
            [1.0, 0.999999999999987, 0.0],
            [1.0, 1.0, 0.864664716763387],
            [1.0, 0.999999999999987, 0.0],
            [0.0, 0.0, 0.0],
            [1.0, 1.0, 0.864664716763387],
            [0.0, 0.0, 0.0],
            [1.0, 0.999999999999987, 0.0],
            [1.0, 1.0, 0.864664716763387],
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
            [1.0, 1.0, 0.864664716763387],
        ],
        index=alternatives,
        columns=profiles,
    )

    DM1_g5_alternatives_partial_preferences = pd.DataFrame(
        [
            [1.0, 1.0, 0.0],
            [0.166666666666667, 0.0, 0.0],
            [1.0, 0.166666666666667, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.166666666666667],
            [1.0, 1.0, 0.0],
            [1.0, 0.166666666666667, 0.0],
            [1.0, 1.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
        ],
        index=alternatives,
        columns=profiles,
    )

    DM1_alternatives_partial_preferences = pd.concat(
        [
            DM1_g1_alternatives_partial_preferences,
            DM1_g2_alternatives_partial_preferences,
            DM1_g3_alternatives_partial_preferences,
            DM1_g4_alternatives_partial_preferences,
            DM1_g5_alternatives_partial_preferences,
        ],
        keys=criteria,
    )

    DM1_partial_preferences = (
        DM1_alternatives_partial_preferences,
        DM1_profiles_partial_preferences,
    )

    DM2_g1_profiles_partial_preferences = pd.DataFrame(
        [
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.3, 0.5, 0.5, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0],
            [1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 1.0, 0.9, 0.3, 1.0, 1.0, 0.3],
        ],
        index=profiles,
        columns=alternatives,
    )

    DM2_g2_profiles_partial_preferences = pd.DataFrame(
        [
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.7, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
            [1.0, 1.0, 1.0, 1.0, 0.0, 1.0, 1.0, 0.5, 1.0, 1.0, 1.0, 0.5],
        ],
        index=profiles,
        columns=alternatives,
    )

    DM2_g3_profiles_partial_preferences = pd.DataFrame(
        [
            [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.285714285714286,
                0.0,
                0.0,
                0.285714285714286,
                0.0,
                0.285714285714286,
                0.0,
            ],
            [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                0.0,
                1.0,
                0.714285714285714,
                1.0,
                0.0,
            ],
            [
                0.714285714285714,
                0.0,
                0.0,
                1.0,
                1.0,
                1.0,
                1.0,
                0.428571428571429,
                1.0,
                1.0,
                1.0,
                0.142857142857143,
            ],
        ],
        index=profiles,
        columns=alternatives,
    )

    DM2_g4_profiles_partial_preferences = pd.DataFrame(
        [
            [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.999664537372098,
                0.0,
                0.0,
                0.0,
                0.0,
                0.999664537372098,
                0.0,
            ],
            [
                0.0,
                0.0,
                0.0,
                0.999999999999987,
                0.0,
                1.0,
                0.0,
                0.0,
                1.0,
                1.0,
                1.0,
                0.0,
            ],
            [
                0.393469340287367,
                0.0,
                0.393469340287367,
                1.0,
                0.0,
                1.0,
                0.393469340287367,
                0.0,
                1.0,
                1.0,
                1.0,
                0.0,
            ],
        ],
        index=profiles,
        columns=alternatives,
    )

    DM2_g5_profiles_partial_preferences = pd.DataFrame(
        [
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,
                0.166666666666667,
                0.0,
            ],
            [
                0.0,
                1.0,
                0.166666666666667,
                1.0,
                0.0,
                0.0,
                0.166666666666667,
                0.0,
                0.0,
                1.0,
                1.0,
                0.0,
            ],
        ],
        index=profiles,
        columns=alternatives,
    )

    DM2_profiles_partial_preferences = pd.concat(
        [
            DM2_g1_profiles_partial_preferences,
            DM2_g2_profiles_partial_preferences,
            DM2_g3_profiles_partial_preferences,
            DM2_g4_profiles_partial_preferences,
            DM2_g5_profiles_partial_preferences,
        ],
        keys=criteria,
    )

    DM2_g1_alternatives_partial_preferences = pd.DataFrame(
        [
            [1.0, 0.9, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [1.0, 0.5, 0.0],
            [1.0, 1.0, 0.0],
            [1.0, 1.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
        ],
        index=alternatives,
        columns=profiles,
    )

    DM2_g2_alternatives_partial_preferences = pd.DataFrame(
        [
            [1.0, 0.8, 0.0],
            [1.0, 0.3, 0.0],
            [1.0, 0.7, 0.0],
            [0.3, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [1.0, 1.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [1.0, 1.0, 0.0],
        ],
        index=alternatives,
        columns=profiles,
    )

    DM2_g3_alternatives_partial_preferences = pd.DataFrame(
        [
            [1.0, 1.0, 0.0],
            [1.0, 1.0, 0.0],
            [1.0, 1.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 0.714285714285714, 0.0],
            [0.0, 0.0, 0.0],
            [1.0, 0.714285714285714, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 0.0, 0.0],
            [0.428571428571429, 0.0, 0.0],
            [0.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
        ],
        index=alternatives,
        columns=profiles,
    )

    DM2_g4_alternatives_partial_preferences = pd.DataFrame(
        [
            [1.0, 1.0, 0.0],
            [1.0, 1.0, 0.393469340287367],
            [1.0, 1.0, 0.0],
            [0.988891003461758, 0.0, 0.0],
            [1.0, 1.0, 0.393469340287367],
            [0.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [1.0, 1.0, 0.393469340287367],
            [0.864664716763387, 0.0, 0.0],
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
            [1.0, 1.0, 0.393469340287367],
        ],
        index=alternatives,
        columns=profiles,
    )

    DM2_g5_alternatives_partial_preferences = pd.DataFrame(
        [
            [1.0, 1.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [1.0, 0.166666666666667, 0.0],
            [1.0, 1.0, 1.0],
            [1.0, 1.0, 0.0],
            [1.0, 1.0, 0.0],
            [1.0, 1.0, 0.0],
            [1.0, 1.0, 0.166666666666667],
            [0.0, 0.0, 0.0],
            [0.166666666666667, 0.0, 0.0],
            [1.0, 1.0, 0.166666666666667],
        ],
        index=alternatives,
        columns=profiles,
    )

    DM2_alternatives_partial_preferences = pd.concat(
        [
            DM2_g1_alternatives_partial_preferences,
            DM2_g2_alternatives_partial_preferences,
            DM2_g3_alternatives_partial_preferences,
            DM2_g4_alternatives_partial_preferences,
            DM2_g5_alternatives_partial_preferences,
        ],
        keys=criteria,
    )

    DM2_partial_preferences = (
        DM2_alternatives_partial_preferences,
        DM2_profiles_partial_preferences,
    )

    return [DM1_partial_preferences, DM2_partial_preferences]


@pytest.fixture
def dms_profile_vs_profile_partial_preferences():
    dms = ["DM1", "DM2"]
    profiles = [f"p{i}" for i in range(1, 4)]
    criteria = [f"g{i}" for i in range(1, 6)]

    dm_profile_index = pd.MultiIndex.from_product([dms, profiles])

    g1_profile_vs_profile_partial_preferences = pd.DataFrame(
        [
            [0.0, 0.0, 0.0, 0.5, 0.0, 0.0],
            [1.0, 0.0, 0.0, 1.0, 0.5, 0.0],
            [1.0, 1.0, 0.0, 1.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0, 1.0, 0.0, 0.0],
            [1.0, 1.0, 0.5, 1.0, 1.0, 0.0],
        ],
        index=dm_profile_index,
        columns=dm_profile_index,
    )

    g2_profile_vs_profile_partial_preferences = pd.DataFrame(
        [
            [0.0, 0.0, 0.0, 0.5, 0.0, 0.0],
            [1.0, 0.0, 0.0, 1.0, 0.5, 0.0],
            [1.0, 1.0, 0.0, 1.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.5, 0.0, 0.0, 1.0, 0.0, 0.0],
            [1.0, 1.0, 0.5, 1.0, 1.0, 0.0],
        ],
        index=dm_profile_index,
        columns=dm_profile_index,
    )

    g3_profile_vs_profile_partial_preferences = pd.DataFrame(
        [
            [0.0, 0.0, 0.0, 0.428571428571429, 0.0, 0.0],
            [1.0, 0.0, 0.0, 1.0, 0.285714285714286, 0.0],
            [1.0, 1.0, 0.0, 1.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.714285714285714, 0.0, 0.0, 1.0, 0.0, 0.0],
            [1.0, 1.0, 0.142857142857143, 1.0, 1.0, 0.0],
        ],
        index=dm_profile_index,
        columns=dm_profile_index,
    )

    g4_profile_vs_profile_partial_preferences = pd.DataFrame(
        [
            [0.0, 0.0, 0.0, 0.988891003461758, 0.0, 0.0],
            [1.0, 0.0, 0.0, 1.0, 0.864664716763387, 0.0],
            [1.0, 0.999999999999987, 0.0, 1.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.999999999999987, 0.0, 0.0, 1.0, 0.0, 0.0],
            [1.0, 1.0, 0.393469340287367, 1.0, 1.0, 0.0],
        ],
        index=dm_profile_index,
        columns=dm_profile_index,
    )

    g5_profile_vs_profile_partial_preferences = pd.DataFrame(
        [
            [0.0, 0.0, 0.0, 0.166666666666667, 0.0, 0.0],
            [1.0, 0.0, 0.0, 1.0, 0.166666666666667, 0.0],
            [1.0, 1.0, 0.0, 1.0, 1.0, 0.166666666666667],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.166666666666667, 0.0, 0.0, 1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0, 1.0, 1.0, 0.0],
        ],
        index=dm_profile_index,
        columns=dm_profile_index,
    )

    return pd.concat(
        [
            g1_profile_vs_profile_partial_preferences,
            g2_profile_vs_profile_partial_preferences,
            g3_profile_vs_profile_partial_preferences,
            g4_profile_vs_profile_partial_preferences,
            g5_profile_vs_profile_partial_preferences,
        ],
        keys=criteria,
    )


@pytest.fixture
def criteria_weights():
    criteria = [f"g{i}" for i in range(1, 6)]
    return pd.Series(
        [
            0.283018867924528,
            0.188679245283019,
            0.188679245283019,
            0.188679245283019,
            0.150943396226415,
        ],
        index=criteria,
    )


def test_calculate_gdss_flows(
    dms_partial_preferences,
    dms_profile_vs_profile_partial_preferences,
    criteria_weights,
):
    alternatives = [f"a{i}" for i in range(1, 13)]
    dms = ["DM1", "DM2"]
    profiles = [f"p{i}" for i in range(1, 4)]

    expected_alternatives_general_net_flows = pd.Series(
        [
            0.41492534269836,
            0.201289031443645,
            0.234257478068232,
            -0.316012711780927,
            0.378437878403812,
            -0.0214779204617149,
            0.191804647879552,
            0.583663994007286,
            0.0834757455914891,
            -0.600878573034886,
            -0.382064922558151,
            0.685490888287011,
        ],
        index=alternatives,
    )

    profiles_general_net_flows_index = pd.MultiIndex.from_product([dms, profiles])

    expected_profiles_general_net_flows = pd.DataFrame(
        [
            [
                -0.313930546691442,
                -0.349420214256582,
                -0.334146180114623,
                -0.401146565174307,
                -0.334146180114623,
                -0.414046064596101,
                -0.327407635640229,
                -0.313930546691442,
                -0.39769752929449,
                -0.480297779489154,
                -0.43560940691416,
                -0.313930546691442,
            ],
            [
                0.164173994419242,
                0.0808727493929295,
                0.090755947955373,
                -0.0337466832858023,
                0.114886354835106,
                0.0898574753587876,
                0.09691690290339,
                0.194978769159327,
                0.0898574753587876,
                -0.0745630098164146,
                -0.0139161095468728,
                0.211151275897871,
            ],
            [
                0.464750537612585,
                0.465081636383001,
                0.44716614536512,
                0.384016357147946,
                0.49986536119368,
                0.455894164874811,
                0.410970535045521,
                0.522712235792576,
                0.467574308630426,
                0.384016357147946,
                0.397493446096733,
                0.558266079971757,
            ],
            [
                -0.50406457588589,
                -0.50406457588589,
                -0.50406457588589,
                -0.523231934283147,
                -0.50406457588589,
                -0.592619261144283,
                -0.50406457588589,
                -0.50406457588589,
                -0.542367798768664,
                -0.59493866136914,
                -0.610588713075999,
                -0.50406457588589,
            ],
            [
                0.0259813129867393,
                -0.0575766384957405,
                -0.0333178783879237,
                -0.169885713068966,
                -0.0329328187036727,
                -0.0724014363394062,
                -0.0194557297548856,
                0.0354152752508903,
                -0.0724014363394062,
                -0.222382183355194,
                -0.13798993589017,
                0.0354152752508903,
            ],
            [
                0.518739571300218,
                0.537640498385406,
                0.534398665126428,
                0.47312649999491,
                0.580767183021524,
                0.51490547573615,
                0.507444487228854,
                0.565172265809356,
                0.526585619491766,
                0.47312649999491,
                0.47312649999491,
                0.600726109988537,
            ],
        ],
        index=profiles_general_net_flows_index,
        columns=alternatives,
    )

    (
        actual_alternatives_general_net_flows,
        actual_profiles_general_net_flows,
    ) = calculate_gdss_flows(
        dms_partial_preferences,
        dms_profile_vs_profile_partial_preferences,
        criteria_weights,
    )

    assert_series_equal(
        expected_alternatives_general_net_flows,
        actual_alternatives_general_net_flows,
        atol=0.006,
    )
    assert_frame_equal(
        expected_profiles_general_net_flows,
        actual_profiles_general_net_flows,
        atol=0.006,
    )
