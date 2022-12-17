import pytest
import sys
import pandas as pd
from pandas.testing import assert_frame_equal
from modular_parts.flows import calculate_promethee_outranking_flows
from core.enums import FlowType

sys.path.append('../..')


@pytest.fixture
def alternatives_preferences():
    alternatives = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']
    return pd.DataFrame([[0, 0.06554, 0.02185, 0.07647, 0, 0.04370],
                         [0.36323, 0, 0, 0.01092, 0, 0.23526],
                         [0.5586, 0.23632, 0, 0.05462, 0.04697, 0.44973],
                         [0.92353, 0.56030, 0.36767, 0, 0.39967, 0.79555],
                         [0.52386, 0.22617, 0.03683, 0.07647, 0, 0.43958],
                         [0.12798, 0.02185, 0, 0.03277, 0, 0]],
                        index=alternatives, columns=alternatives)


@pytest.fixture
def alternatives_vs_profiles_preferences():
    alternatives = [f"a{i}" for i in range(1, 13)]
    profiles = [f"p{i}" for i in range(1, 4)]
    alternatives_preferences = pd.DataFrame([[1.0, 0.671159029649593, 0.0],
                                             [0.751572327044025,
                                              0.377358490566038,
                                              0.190098464079345],
                                             [0.858490566037736,
                                              0.440251572327042,
                                              0.0269541778975741],
                                             [0.42722371967655, 0.0, 0.0],
                                             [0.858490566037736,
                                              0.609164420485175,
                                              0.282641141527683],
                                             [0.622641509433962,
                                              0.528301886792453, 0.0],
                                             [0.905660377358491,
                                              0.294699011680141, 0.0],
                                             [1.0, 0.886792452830189,
                                              0.163144286181771],
                                             [0.622641509433962,
                                              0.528301886792453,
                                              0.0566037735849057],
                                             [0.141509433962264, 0.0, 0.0],
                                             [0.471698113207547,
                                              0.0943396226415094, 0.0],
                                             [1.0, 1.0, 0.219748059766677]],
                                            index=alternatives,
                                            columns=profiles)
    profiles_preferences = pd.DataFrame(
        [[0.0, 0.0, 0.0, 0.0377358490566038, 0.0, 0.323450134766569, 0.0, 0.0,
          0.209010387655298, 0.306080063546244, 0.323450134766569, 0.0],
         [0.0, 0.289308176100629, 0.283018867924528, 0.714285714285714,
          0.283018867924528, 0.377358490566038, 0.0943396226415094, 0.0,
          0.377358490566038, 1.0, 0.669811320754717, 0.0],
         [0.434860736747529, 0.622641509433962, 0.584905660377358, 1.0,
          0.471698113207547, 0.49685534591195, 0.811320754716981,
          0.192273135669362,
          0.471698113207547, 1.0, 0.905660377358491, 0.0]], index=profiles,
        columns=alternatives)
    return alternatives_preferences, profiles_preferences


@pytest.fixture
def alternatives_vs_profiles_preferences():
    alternatives = [f"a{i}" for i in range(1, 13)]
    profiles = [f"p{i}" for i in range(1, 4)]
    alternatives_preferences = pd.DataFrame([[1.0, 0.671159029649593, 0.0],
                                             [0.751572327044025,
                                              0.377358490566038,
                                              0.190098464079345],
                                             [0.858490566037736,
                                              0.440251572327042,
                                              0.0269541778975741],
                                             [0.42722371967655, 0.0, 0.0],
                                             [0.858490566037736,
                                              0.609164420485175,
                                              0.282641141527683],
                                             [0.622641509433962,
                                              0.528301886792453, 0.0],
                                             [0.905660377358491,
                                              0.294699011680141, 0.0],
                                             [1.0, 0.886792452830189,
                                              0.163144286181771],
                                             [0.622641509433962,
                                              0.528301886792453,
                                              0.0566037735849057],
                                             [0.141509433962264, 0.0, 0.0],
                                             [0.471698113207547,
                                              0.0943396226415094, 0.0],
                                             [1.0, 1.0, 0.219748059766677]],
                                            index=alternatives,
                                            columns=profiles)
    profiles_preferences = pd.DataFrame(
        [[0.0, 0.0, 0.0, 0.0377358490566038, 0.0, 0.323450134766569, 0.0, 0.0,
          0.209010387655298, 0.306080063546244, 0.323450134766569, 0.0],
         [0.0, 0.289308176100629, 0.283018867924528, 0.714285714285714,
          0.283018867924528, 0.377358490566038, 0.0943396226415094, 0.0,
          0.377358490566038, 1.0, 0.669811320754717, 0.0],
         [0.434860736747529, 0.622641509433962, 0.584905660377358, 1.0,
          0.471698113207547, 0.49685534591195, 0.811320754716981,
          0.192273135669362,
          0.471698113207547, 1.0, 0.905660377358491, 0.0]], index=profiles,
        columns=alternatives)
    return alternatives_preferences, profiles_preferences


@pytest.fixture
def alternatives_vs_profiles_preferencesII():
    alternatives = [f"a{i}" for i in range(1, 4)]
    profiles = [f"p{i}" for i in range(1, 5)]
    alternatives_preferences = pd.DataFrame([[0.97, 0.8, 0.38, 0.0],
                                             [0.36, 0.0, 0.0, 0.0],
                                             [1.0, 0.6, 0.4, 0.0]],
                                            index=alternatives,
                                            columns=profiles)
    profiles_preferences = pd.DataFrame([[0.0, 0.0, 0.0],
                                         [0.2, 0.95, 0.31],
                                         [0.4, 1.0, 0.6],
                                         [1.0, 1.0, 0.69]], index=profiles,
                                        columns=alternatives)
    return alternatives_preferences, profiles_preferences


@pytest.fixture
def profiles_preferences():
    profiles = [f"p{i}" for i in range(1, 5)]
    return pd.DataFrame([[0.0, 0.0, 0.0, 0.0],
                         [1.0, 0.0, 0.0, 0.0],
                         [1.0, 1.0, 0.0, 0.0],
                         [1.0, 1.0, 1.0, 0.0]], index=profiles,
                        columns=profiles)


def test_basic_outranking_flows(alternatives_preferences):
    alternatives = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6']
    expected = pd.DataFrame({'positive': [0.041512, 0.121882, 0.269248,
                                          0.609344, 0.260582, 0.03652],
                             'negative': [0.49944, 0.222036, 0.08527, 0.05025,
                                          0.089328, 0.392764]
                             }, index=alternatives)

    actual = calculate_promethee_outranking_flows(alternatives_preferences,
                                                  FlowType.BASIC)

    assert_frame_equal(expected, actual, atol=0.006)


def test_profile_based_outranking_flows(alternatives_vs_profiles_preferencesII,
                                        profiles_preferences):
    alternatives = [f"a{i}" for i in range(1, 4)]
    profiles = [f"p{i}" for i in range(1, 5)]
    external_index = []
    internal_index = []
    for alternative in alternatives:
        external_index += [f"R{alternative}"] * (len(profiles) + 1)
        internal_index += profiles + [alternative]

    flows_index = pd.MultiIndex.from_arrays([external_index, internal_index])

    expected = pd.DataFrame({'positive': [0.0, 0.3, 0.6, 1, 0.54,
                                          0.0, 0.49, 0.75, 1.0, 0.09,
                                          0.0, 0.33, 0.65, 0.92, 0.5],
                             'negative': [0.99, 0.7, 0.34, 0.0, 0.4,
                                          0.84, 0.5, 0.25, 0.0, 0.74,
                                          1.0, 0.65, 0.35, 0.0, 0.4]},
                            index=flows_index)

    actual = calculate_promethee_outranking_flows(
        alternatives_vs_profiles_preferencesII,
        FlowType.PROFILE_BASED, profiles_preferences)
    assert_frame_equal(expected, actual, atol=0.006)


def test_basic_outranking_flows_for_alternatives_vs_profiles(
        alternatives_vs_profiles_preferences):
    alternatives = [f"a{i}" for i in range(1, 13)]
    profiles = [f"p{i}" for i in range(1, 4)]
    expected_alternatives = pd.DataFrame({'positive': [0.557053009883198,
                                                       0.439676427229803,
                                                       0.441898772087451,
                                                       0.14240790655885,
                                                       0.583432042683531,
                                                       0.383647798742138,
                                                       0.400119796346211,
                                                       0.68331224633732,
                                                       0.40251572327044,
                                                       0.0471698113207547,
                                                       0.188679245283019,
                                                       0.739916019922226],
                                          'negative': [0.144953578915843,
                                                       0.30398322851153,
                                                       0.289308176100629,
                                                       0.584007187780773,
                                                       0.251572327044025,
                                                       0.399221323748186,
                                                       0.30188679245283,
                                                       0.0640910452231207,
                                                       0.352688997142961,
                                                       0.768693354515415,
                                                       0.632973944293259, 0.0]
                                          }, index=alternatives)

    actual_alternatives = calculate_promethee_outranking_flows(
        alternatives_vs_profiles_preferences,
        FlowType.BASIC)
    assert_frame_equal(expected_alternatives, actual_alternatives, atol=0.006)

    expected_profiles = pd.DataFrame(
        {'positive': [0.0999772141492737, 0.340708295896975,
                      0.582659478885894],
         'negative': [0.721660676849356, 0.452530697813716, 0.078265825253163]
         }, index=profiles)
    actual_profiles = calculate_promethee_outranking_flows(
        alternatives_vs_profiles_preferences[::-1],
        flow_type=FlowType.BASIC)
    assert_frame_equal(expected_profiles, actual_profiles, atol=0.006)


if __name__ == '__main__':
    test_basic_outranking_flows(alternatives_preferences)
    test_profile_based_outranking_flows(alternatives_vs_profiles_preferencesII,
                                        profiles_preferences)
    test_basic_outranking_flows_for_alternatives_vs_profiles(
        alternatives_vs_profiles_preferences)
