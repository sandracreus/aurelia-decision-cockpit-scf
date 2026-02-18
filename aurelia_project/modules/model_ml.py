import numpy as np
from dataclasses import dataclass
 
 
@dataclass
class DemandPrediction:
    demand: float
    base: float
    rain_effect: float
    promo_effect: float
    noise: float
 
 
def predict_demand(day_of_week: int, rain: float, promo: bool, base: float = 100.0, seed: int = 42) -> DemandPrediction:
    """
    Predictor simulado.
    day_of_week: 0..6
    rain: 0..1 (0=sol, 1=lluvia)
    promo: True/False
    """
    rng = np.random.default_rng(seed + int(day_of_week))
    noise = float(rng.normal(loc=0.0, scale=5.0))
 
    rain_effect = float(rain * 20.0)
    promo_effect = float(50.0 if promo else 0.0)
    demand = float(base + rain_effect + promo_effect + noise)
 
    return DemandPrediction(
        demand=demand,
        base=base,
        rain_effect=rain_effect,
        promo_effect=promo_effect,
        noise=noise,
    )
