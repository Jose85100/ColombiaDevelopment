"""Synthetic infrastructure planning kernels. No operational infrastructure claims."""
from dataclasses import dataclass

@dataclass(frozen=True)
class DataCenter:
    it_mw: float
    pue: float
    utilization: float
    price_usd_per_kw_month: float
    energy_usd_per_mwh: float

def data_center_annual(c: DataCenter):
    if c.it_mw <= 0 or c.pue < 1 or not 0 <= c.utilization <= 1 or c.price_usd_per_kw_month < 0 or c.energy_usd_per_mwh < 0:
        raise ValueError("invalid data center inputs")
    facility_mwh = c.it_mw * c.pue * 8760
    billed_kw = c.it_mw * 1000 * c.utilization
    revenue = billed_kw * c.price_usd_per_kw_month * 12
    energy_cost = facility_mwh * c.energy_usd_per_mwh
    return {"facility_mwh": facility_mwh, "revenue_usd": revenue, "energy_cost_usd": energy_cost, "energy_margin_usd": revenue-energy_cost}

def intermodal_cost(tons: float, legs: list[tuple[float,float]], transfer_cost_per_ton: float=0):
    """Legs are (distance_km, cost_per_ton_km). Returns total USD or COP consistently with input unit."""
    if tons < 0 or transfer_cost_per_ton < 0 or any(d < 0 or rate < 0 for d,rate in legs):
        raise ValueError("negative logistics input")
    return tons * (sum(d*rate for d,rate in legs) + transfer_cost_per_ton)
