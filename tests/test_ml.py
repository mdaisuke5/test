import pytest
from trading.ml import MLModel


def test_ml_predict_returns_average():
    model = MLModel()
    assert model.predict([1, 2, 3]) == 2


def test_ml_predict_empty_data():
    model = MLModel()
    with pytest.raises(ValueError):
        model.predict([])
