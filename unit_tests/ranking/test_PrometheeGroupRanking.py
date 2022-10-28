import pytest
import sys
import pandas as pd
from pandas.testing import assert_frame_equal
from modular_parts.flows import calculate_promethee_group_ranking

sys.path.append('../..')


# TODO Fix returned DF
@pytest.fixture
def dms_data_frame():
    dms = ['DM1', 'DM2', 'DM3', 'DM4']
    return pd.DataFrame({'weights': [1, 1, 1, 1],
                         'flows': [[-0.40, 0.23, 0.06, -0.19, 0.28, 0.02],
                                   [0.21, 0.10, -0.19, 0.37, -0.21, -0.29],
                                   [0.28, 0.28, -0.25, -0.05, -0.42, 0.17],
                                   [-0.16, 0.09, 0.38, -0.20, -0.11, -0.01]]}, index=dms)


# TODO Write test function
def test_promethee_group_ranking(dms_data_frame):
    pass


if __name__ == '__main__':
    test_promethee_group_ranking(dms_data_frame)
