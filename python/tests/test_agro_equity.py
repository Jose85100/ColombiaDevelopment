from colombia_dev.agro_equity import Ownership,AgroScenario,equity_after_round,operating_result,hypothetical_distribution

def test_cap_table_conservation():
    result=equity_after_round(Ownership(),100,25)
    assert abs(sum(result.values())-1)<1e-12
    assert result['farmers']<.55

def test_farmer_pro_rata_reduces_dilution():
    a=equity_after_round(Ownership(),100,25)
    b=equity_after_round(Ownership(),100,25,10)
    assert b['farmers']>a['farmers']

def test_operating_result():
    r=operating_result(AgroScenario(10,5,100,100,10,200,.10))
    assert r['saleable_tons']==45
    assert r['revenue']==4500

def test_distribution_conservation():
    r=hypothetical_distribution(1000,.4,Ownership())
    assert abs(sum(r.values())-1000)<1e-9
