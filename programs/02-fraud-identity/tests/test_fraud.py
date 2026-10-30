from colombia_dev.fraud import Signals, score as fraud_score

def test_fraud_monotonic_extremes():
    lo = fraud_score(Signals(0, 0, 0, 0, 0, 0))["fraud_probability"]
    hi = fraud_score(Signals(1, 1, 1, 1, 1, 1))["fraud_probability"]
    assert hi > lo
