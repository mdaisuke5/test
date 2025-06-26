from trading.logic import should_buy


def test_should_buy_above_ma():
    assert should_buy(105, 100)


def test_should_not_buy_below_ma():
    assert not should_buy(95, 100)
