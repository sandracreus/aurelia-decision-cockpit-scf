from dataclasses import dataclass, asdict
from typing import List, Dict
 
 
@dataclass
class ProblemSpec:
    S: str  # State
    A: str  # Actions
    T: str  # Transitions
    G: str  # Goals
    C: str  # Constraints (texto libre)
    R: str  # Rewards / Risks / Results
    hard_constraints: List[str]
    soft_constraints: List[str]
 
    def to_markdown(self) -> str:
        hard = "\n".join([f"- {x}" for x in self.hard_constraints]) or "- (ninguna)"
        soft = "\n".join([f"- {x}" for x in self.soft_constraints]) or "- (ninguna)"
        return f"""
## Ficha del Problema (State Card)
 
**S (Estado):**  
{self.S}
 
**A (Acciones):**  
{self.A}
 
**T (Transiciones):**  
{self.T}
 
**G (Objetivos):**  
{self.G}
 
**C (Restricciones - texto libre):**  
{self.C}
 
**Hard constraints (checkbox):**  
{hard}
 
**Soft constraints (checkbox):**  
{soft}
 
**R (Riesgos/Recompensa/Resultado):**  
{self.R}
""".strip()
 
    def to_dict(self) -> Dict:
        return asdict(self)
