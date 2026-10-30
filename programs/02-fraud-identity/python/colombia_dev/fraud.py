from dataclasses import dataclass
from math import exp

@dataclass(frozen=True)
class Signals:
    identity: float; device: float; velocity: float; behavioral: float; document: float; graph: float

def _clip(x): return max(0.0,min(1.0,float(x)))
def score(s: Signals):
    x=[_clip(v) for v in (s.identity,s.device,s.velocity,s.behavioral,s.document,s.graph)]
    z=-3.2+sum(w*v for w,v in zip((1.35,1.15,1.10,.75,1.25,1.55),x))
    p=1/(1+exp(-z))
    action="REVIEW" if p>=.65 else "STEP_UP" if p>=.30 else "ALLOW"
    return {"fraud_probability":p,"action":action,"signals":x}

def counterfactual(s: Signals, field: str, value: float):
    d=s.__dict__.copy(); d[field]=value
    before,after=score(s),score(Signals(**d))
    return {"before":before,"after":after,"delta":after["fraud_probability"]-before["fraud_probability"]}
