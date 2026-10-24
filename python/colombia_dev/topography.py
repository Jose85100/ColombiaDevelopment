"""Rail topographic screening using a sampled metric profile (not engineering design)."""
from math import hypot, isfinite

def profile_metrics(points, max_grade=0.015):
    """points: sequence of (distance_m, elevation_m) in an engineering-consistent vertical datum."""
    if len(points)<2 or not 0<max_grade<1:
        raise ValueError("invalid profile")
    grades=[]; flagged=[]; cumulative=0.0
    for i in range(1,len(points)):
        x0,z0=points[i-1];x1,z1=points[i]
        if not all(isfinite(v) for v in (x0,z0,x1,z1)) or x1<=x0:
            raise ValueError("distance must increase and values must be finite")
        dx=x1-x0;dz=z1-z0;grade=dz/dx
        grades.append(grade);cumulative+=hypot(dx,dz)
        if abs(grade)>max_grade:flagged.append(i)
    return {"grades":grades,"max_abs_grade":max(abs(g) for g in grades),"segments_above_limit":flagged,"profile_length_m":cumulative}

def interpolate_profile(points,step_m):
    if step_m<=0 or len(points)<2:raise ValueError("invalid step")
    result=[points[0]]
    for (x0,z0),(x1,z1) in zip(points,points[1:]):
        if x1<=x0:raise ValueError("distance must increase")
        x=x0+step_m
        while x<x1:
            result.append((x,z0+(z1-z0)*(x-x0)/(x1-x0)))
            x+=step_m
        result.append((x1,z1))
    return result
