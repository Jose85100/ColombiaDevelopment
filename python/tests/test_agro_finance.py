from dataclasses import replace
from colombia_dev.agro_finance import Project,evaluate

def test_more_price_increases_npv():
    p=Project()
    assert evaluate(replace(p,sale_price_mcop_ton=3))['npv_mcop']>evaluate(p)['npv_mcop']

def test_water_constraint():
    assert not evaluate(replace(Project(),max_water_m3_year=100))['water_within_cap']

def test_15_15_headcount():
    r=evaluate(Project(staff_per_rotation=12))
    assert r['headcount_assumed']==24

def test_cost_of_capital():
    p=Project()
    assert evaluate(replace(p,discount_rate=.25))['npv_mcop']<evaluate(p)['npv_mcop']
