from dataclasses import dataclass
from typing import List
 
 
@dataclass
class Package:
    pkg_id: str
    weight: float
    value: float
 
 
@dataclass
class ORSolution:
    selected: List[Package]
    total_weight: float
    total_value: float
    utilization: float  # 0..1
 
 
def greedy_select(capacity: float, packages: List[Package], mode: str = "value") -> ORSolution:
    """
    Optimizador greedy tipo knapsack.
    mode: 'value' (por valor) o 'ratio' (valor/peso)
    """
    if capacity <= 0:
        return ORSolution([], 0.0, 0.0, 0.0)
 
    if mode == "ratio":
        ranked = sorted(
            packages,
            key=lambda p: (p.value / p.weight) if p.weight > 0 else 0.0,
            reverse=True,
        )
    else:
        ranked = sorted(packages, key=lambda p: p.value, reverse=True)
 
    selected = []
    total_w = 0.0
    total_v = 0.0
 
    for p in ranked:
        if total_w + p.weight <= capacity:
            selected.append(p)
            total_w += p.weight
            total_v += p.value
 
    return ORSolution(
        selected=selected,
        total_weight=total_w,
        total_value=total_v,
        utilization=min(total_w / capacity, 1.0),
    )
