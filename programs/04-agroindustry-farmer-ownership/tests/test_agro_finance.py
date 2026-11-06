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
    # Con flujos positivos, un costo de capital mayor reduce el VPN. (Con los parámetros base los flujos son
    # negativos y el efecto se invierte: ver test_base_case_is_not_viable.)
    p=replace(Project(),sale_price_mcop_ton=6.0)
    assert evaluate(p)['npv_mcop']>0
    assert evaluate(replace(p,discount_rate=.25))['npv_mcop']<evaluate(p)['npv_mcop']

def test_base_case_is_not_viable():
    # Hallazgo documentado: con los parámetros sintéticos por defecto el proyecto no se sostiene.
    r=evaluate(Project())
    assert r['npv_mcop']<0
    assert r['year1']['ebitda_mcop']<0
    assert r['annual_staff_cost_mcop']/r['year1']['revenue_mcop']>0.7

def test_break_even_price_is_about_twice_the_base_price():
    lo,hi=0.1,50.0
    for _ in range(80):
        m=(lo+hi)/2
        if evaluate(replace(Project(),sale_price_mcop_ton=m))['npv_mcop']<0:lo=m
        else:hi=m
    assert 4.9<hi<5.1
