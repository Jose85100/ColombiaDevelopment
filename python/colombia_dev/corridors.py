"""Transparent multi-criteria screening of conceptual transport corridors."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Corridor:
    name: str
    capex_index: float
    travel_time_index: float
    geology_risk: float
    flood_risk: float
    social_environmental_risk: float
    demand_index: float
    prohibited: bool = False

def rank_corridors(items, weights=None):
    """All indices 0..1, lower is better except demand. Exclusions are non-compensatory."""
    weights=weights or {"capex_index":.25,"travel_time_index":.15,"geology_risk":.20,"flood_risk":.15,"social_environmental_risk":.15,"demand_index":.10}
    if any(w<0 or not isfinite(w) for w in weights.values()) or abs(sum(weights.values())-1)>1e-9:
        raise ValueError("weights must be nonnegative and sum to 1")
    if set(weights)!={"capex_index","travel_time_index","geology_risk","flood_risk","social_environmental_risk","demand_index"}:
        raise ValueError("invalid weight keys")
    result=[]
    for c in items:
        values={k:getattr(c,k) for k in weights}
        if any(not isfinite(v) or not 0<=v<=1 for v in values.values()):
            raise ValueError("all indices must be in [0,1]")
        penalty=sum(weights[k]*(1-v if k=="demand_index" else v) for k,v in values.items())
        result.append({"name":c.name,"feasible":not c.prohibited,"penalty":penalty,"status":"EXCLUDED" if c.prohibited else "SCREENING"})
    return sorted(result,key=lambda x:(not x["feasible"],x["penalty"]))
