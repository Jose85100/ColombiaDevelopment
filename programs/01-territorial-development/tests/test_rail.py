from colombia_dev.rail import RailScenario,evaluate,annual_capacity

def test_zero_cashflow_npv():
    x=evaluate(RailScenario(0,0,0,0,0,100,.1,5))
    assert x["npv"]==-100

def test_growth_increases_npv():
    a=RailScenario(1000,100,2,3,200,10000,.1,10)
    b=RailScenario(1000,100,2,3,200,10000,.1,10,.05)
    assert evaluate(b)["npv"]>evaluate(a)["npv"]

def test_capacity():
    assert annual_capacity(1000,2,300)==600000
