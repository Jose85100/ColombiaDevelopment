from colombia_dev.territorial import Territory, score
from colombia_dev.fraud import Signals, score as fraud_score

def test_territorial_bounds():
    r=score(Territory(.8,.6,.2,.8,.9,.7)); assert all(0<=r[k]<=1 for k in ("vulnerability","opportunity","priority"))
def test_fraud_monotonic_extremes():
    lo=fraud_score(Signals(0,0,0,0,0,0))["fraud_probability"]
    hi=fraud_score(Signals(1,1,1,1,1,1))["fraud_probability"]
    assert hi>lo
