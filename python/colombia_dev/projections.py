"""Deterministic Monte Carlo projection utilities; research use, synthetic defaults."""
from dataclasses import dataclass
from math import exp, sqrt
import random

@dataclass(frozen=True)
class ProjectionConfig:
    initial: float = 100.0
    annual_growth: float = 0.035
    annual_volatility: float = 0.12
    years: int = 10
    paths: int = 5000
    seed: int = 2026

def quantile(values, q):
    if not values or not 0 <= q <= 1:
        raise ValueError("invalid quantile input")
    a = sorted(values)
    pos = (len(a) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(a) - 1)
    return a[lo] + (pos - lo) * (a[hi] - a[lo])

def project(config: ProjectionConfig):
    if config.initial <= 0 or config.years < 1 or config.paths < 2 or config.annual_volatility < 0:
        raise ValueError("invalid projection configuration")
    rng = random.Random(config.seed)
    paths = [config.initial] * config.paths
    out = [{"year": 0, "p05": config.initial, "p50": config.initial, "p95": config.initial, "mean": config.initial}]
    for year in range(1, config.years + 1):
        paths = [x * exp((config.annual_growth - .5 * config.annual_volatility ** 2) + config.annual_volatility * rng.gauss(0, 1)) for x in paths]
        out.append({"year": year, "p05": quantile(paths, .05), "p50": quantile(paths, .5), "p95": quantile(paths, .95), "mean": sum(paths) / len(paths)})
    return out

def forecast_error(actual, predicted):
    if len(actual) != len(predicted) or not actual:
        raise ValueError("mismatched series")
    mae = sum(abs(a-p) for a,p in zip(actual,predicted)) / len(actual)
    rmse = sqrt(sum((a-p)**2 for a,p in zip(actual,predicted)) / len(actual))
    return {"mae": mae, "rmse": rmse}
