from colombia_dev.infrastructure import DataCenter, data_center_annual, intermodal_cost

def test_pue_increases_energy_cost():
    a=data_center_annual(DataCenter(2,1.2,.7,120,90))
    b=data_center_annual(DataCenter(2,1.5,.7,120,90))
    assert b["energy_cost_usd"] > a["energy_cost_usd"]
    assert b["revenue_usd"] == a["revenue_usd"]

def test_intermodal_cost():
    assert intermodal_cost(100,[(10,2),(20,1)],5) == 4500
