import pytest

from rul_audit.generate import generate_fleet
from rul_audit.predictors import all_predictors


@pytest.fixture(scope="module")
def train_fleet():
    return generate_fleet(9001, 60)


@pytest.fixture(scope="module")
def test_fleet():
    return generate_fleet(101, 40)


@pytest.fixture(scope="module")
def fitted_predictors(train_fleet):
    return [p.fit(train_fleet) for p in all_predictors()]
