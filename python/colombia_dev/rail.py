"""Concept-stage rail demand, capacity and project-finance calculations."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class RailScenario:
    annual_tons: float
    passengers: float
    freight_rate_per_ton: float
    fare_per_passenger: float
    operating_cost: float
    capex: float
    discount_rate: float
    horizon: int
    annual_growth: float = 0.0

def evaluate(s: RailScenario):
    values=(s.annual_tons,s.passengers,s.freight_rate_per_ton,s.fare_per_passenger,s.operating_cost,s.capex,s.discount_rate,s.annual_growth)
    if not all(isfinite(v) for v in values) or any(v<0 for v in values[:6]) or s.discount_rate<=-1 or s.annual_growth<=-1 or s.horizon<1:
        raise ValueError("invalid rail scenario")
    cashflows=[-s.capex]
    for t in range(1,s.horizon+1):
        scale=(1+s.annual_growth)**(t-1)
        revenue=scale*(s.annual_tons*s.freight_rate_per_ton+s.passengers*s.fare_per_passenger)
        cashflows.append(revenue-s.operating_cost)
    npv=sum(cf/(1+s.discount_rate)**t for t,cf in enumerate(cashflows))
    return {"npv":npv,"cashflows":cashflows,"year1_revenue":cashflows[1]+s.operating_cost}

def annual_capacity(train_tons:float,trains_per_day:float,operating_days:int=330):
    if min(train_tons,trains_per_day,operating_days)<0 or operating_days>366:
        raise ValueError("invalid capacity")
    return train_tons*trains_per_day*operating_days
