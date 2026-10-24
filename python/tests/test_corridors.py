from colombia_dev.corridors import Corridor,rank_corridors

def test_excluded_corridor_always_last():
    a=Corridor('excluded',0,0,0,0,0,1,True)
    b=Corridor('candidate',.5,.5,.5,.5,.5,.5)
    assert rank_corridors([a,b])[0]['name']=='candidate'

def test_lower_risk_better():
    a=Corridor('low',.5,.5,.1,.1,.1,.5)
    b=Corridor('high',.5,.5,.9,.9,.9,.5)
    assert rank_corridors([b,a])[0]['name']=='low'
