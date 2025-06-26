from trading.risk import RiskGuard


def test_risk_guard_within_limit():
    guard = RiskGuard(max_drawdown=0.1)
    assert guard.check(0.05)


def test_risk_guard_exceeds_limit():
    guard = RiskGuard(max_drawdown=0.1)
    assert not guard.check(0.2)
