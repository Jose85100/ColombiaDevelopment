from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Territory:
    access_gap: float
    climate_hazard: float
    fiscal_capacity: float
    connectivity_gap: float
    renewable_potential: float
    institutional_capacity: float

def _clip(x): return max(0.0,min(1.0,float(x)))
def score(t: Territory):
    v=.30*_clip(t.access_gap)+.20*_clip(t.climate_hazard)+.15*(1-_clip(t.fiscal_capacity))+.20*_clip(t.connectivity_gap)+.15*(1-_clip(t.institutional_capacity))
    o=.45*_clip(t.renewable_potential)+.25*_clip(t.institutional_capacity)+.15*_clip(t.access_gap)+.15*_clip(t.connectivity_gap)
    return {"vulnerability":v,"opportunity":o,"priority":math.sqrt(v*o)}

def robust_priority(t: Territory, shocks=(0.0,.10,.20)):
    base=score(t)
    scenarios=[max(0,base["priority"]-s*base["vulnerability"]) for s in shocks]
    return {**base,"worst_case_priority":min(scenarios),"scenario_priorities":scenarios}
