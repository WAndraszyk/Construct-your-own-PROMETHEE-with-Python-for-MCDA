import pytest
import pandas as pd
from core.constraint import Constraint, Relation
from modular_parts.choice import compute_decision
from pandas.testing import assert_series_equal


@pytest.fixture
def flows():
    alternatives = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'a10', 'a11',
                    'a12', 'a13', 'a14', 'a15', 'a16', 'a17', 'a18', 'a19', 'a20']
    return pd.Series(
        data=[-0.1726, -0.1233, 0.2636, 0.7137, -0.1798, -0.1363, 0.08, 0.0896, 0.076, -0.376,
              0.4747, -0.2428, -0.0187, -0.194, -0.064, -0.1587, -0.0509, -0.0553, 0.2107, -0.136],
        index=alternatives)


@pytest.fixture
def constraints():
    budget = [27, 29, 20, 34, 32, 22, 34, 30, 28, 21, 32, 37, 26, 16, 13, 32, 35, 20, 40, 39]
    return [Constraint(budget, Relation.LT, 150)]


def test_compute_decision(flows, constraints):
    expected = pd.Series(data=['a3', 'a4', 'a11', 'a19'], name='chosen alternatives')
    actual = compute_decision(flows, constraints)

    assert_series_equal(expected, actual)


if __name__ == '__main__':
    test_compute_decision(flows, constraints)
