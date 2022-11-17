import pytest
import sys
import pandas as pd
from pandas.testing import assert_series_equal, assert_frame_equal
from modular_parts.sorting import calculate_alternatives_support

sys.path.append('../..')


@pytest.fixture
def categories():
    return [f"C{i}" for i in range(1, 5)]


@pytest.fixture
def assigments():
    alternatives = [f"a{i}" for i in range(1, 13)]
    DM1_assigments = pd.DataFrame(
        {'worse': ['C3', 'C3', 'C3', 'C1', 'C3', 'C3', 'C3', 'C4', 'C3', 'C1', 'C2', 'C4'],
         'better': ['C3', 'C3', 'C3', 'C1', 'C3', 'C3', 'C3', 'C4', 'C3', 'C1', 'C2', 'C4']}, index=alternatives)

    DM2_assigments = pd.DataFrame(
        {'worse': ['C2', 'C2', 'C3', 'C1', 'C3', 'C3', 'C3', 'C4', 'C3', 'C1', 'C2', 'C4'],
         'better': ['C3', 'C3', 'C3', 'C3', 'C4', 'C3', 'C4', 'C4', 'C3', 'C2', 'C2', 'C4']}, index=alternatives)

    DM3_assigments = pd.DataFrame(
        {'worse': ['C2', 'C2', 'C2', 'C3', 'C2', 'C2', 'C2', 'C3', 'C3', 'C1', 'C1', 'C3'],
         'better': ['C2', 'C2', 'C2', 'C4', 'C2', 'C2', 'C3', 'C4', 'C3', 'C2', 'C2', 'C4']}, index=alternatives)

    DM4_assigments = pd.DataFrame(
        {'worse': ['C1', 'C2', 'C1', 'C3', 'C2', 'C2', 'C1', 'C2', 'C2', 'C1', 'C1', 'C3'],
         'better': ['C2', 'C3', 'C3', 'C4', 'C3', 'C3', 'C3', 'C4', 'C3', 'C3', 'C2', 'C4']}, index=alternatives)

    return [DM1_assigments, DM2_assigments, DM3_assigments, DM4_assigments]


def test_calculate_alternatives_support(categories, assigments):
    alternatives = [f"a{i}" for i in range(1, 13)]
    expected_support = pd.DataFrame([[25.0, 75.0, 50.0, 0.0],
                                     [0.0, 75.0, 75.0, 0.0],
                                     [25.0, 50.0, 75.0, 0.0],
                                     [50.0, 25.0, 75.0, 50.0],
                                     [0.0, 50.0, 75.0, 25.0],
                                     [0.0, 50.0, 75.0, 0.0],
                                     [25.0, 50.0, 100.0, 25.0],
                                     [0.0, 25.0, 50.0, 100.0],
                                     [0.0, 25.0, 100.0, 0.0],
                                     [100.0, 75.0, 25.0, 0.0],
                                     [50.0, 100.0, 0.0, 0.0],
                                     [0.0, 0.0, 50.0, 100.0]], index=alternatives, columns=categories)

    expected_unimodal_support = pd.DataFrame([[25.0, 75.0, 50.0, 0.0],
                                              [0.0, 75.0, 75.0, 0.0],
                                              [25.0, 50.0, 75.0, 0.0],
                                              [50.0, 50.0, 75.0, 50.0],
                                              [0.0, 50.0, 75.0, 25.0],
                                              [0.0, 50.0, 75.0, 0.0],
                                              [25.0, 50.0, 100.0, 25.0],
                                              [0.0, 25.0, 50.0, 100.0],
                                              [0.0, 25.0, 100.0, 0.0],
                                              [100.0, 75.0, 25.0, 0.0],
                                              [50.0, 100.0, 0.0, 0.0],
                                              [0.0, 0.0, 50.0, 100.0]], index=alternatives, columns=categories)

    actual_support, actual_unimodal_support = calculate_alternatives_support(categories, assigments)

    assert_frame_equal(expected_support, actual_support)
    assert_frame_equal(expected_unimodal_support, actual_unimodal_support)


if __name__ == '__main__':
    test_calculate_alternatives_support(categories, assigments)