from dataclasses import dataclass
 
 
@dataclass
class HybridPlan:
    available_minutes: float
    minutes_per_stop: float
    safety_buffer: float
    max_stops: int
 
 
def traffic_from_rain(rain: float) -> float:
    """Convierte lluvia 0..1 en minutos extra por parada."""
    return float(5.0 + 10.0 * rain)  # 5..15
 
 
def plan_route_8h(traffic_minutes: float, risk_level: str, base_stop_minutes: float = 12.0) -> HybridPlan:
    """
    risk_level: 'Conservador' | 'Neutro' | 'Agresivo'
    """
    available = 8.0 * 60.0  # 8h
 
    if risk_level == "Conservador":
        buffer = 0.20
    elif risk_level == "Agresivo":
        buffer = 0.05
    else:
        buffer = 0.10
 
    usable = available * (1.0 - buffer)
    minutes_per_stop = base_stop_minutes + max(0.0, float(traffic_minutes))
    max_stops = int(usable // minutes_per_stop) if minutes_per_stop > 0 else 0
 
    return HybridPlan(
        available_minutes=available,
        minutes_per_stop=minutes_per_stop,
        safety_buffer=buffer,
        max_stops=max_stops,
    )
3.6 cases/catalog.yml
cases:
  - id: "last_mile_basic"
    name: "Última milla - básico"
    context: "Reparto urbano con incertidumbre por clima y promociones."
    S: "Estado: paquetes pendientes, flota disponible, clima, hora."
    A: "Acciones: asignar paquetes a camión, seleccionar ruta, priorizar entregas."
    T: "Transiciones: cambios por tráfico, entregas completadas, incidencias."
    G: "Objetivo: maximizar entregas a tiempo y valor."
    C: "Restricciones: capacidad camión, ventana horaria, normativa."
    R: "Riesgo: retrasos, penalizaciones; recompensa: entregas on-time."
    hard_constraints:
      - "Capacidad del camión"
      - "Ventana horaria"
    soft_constraints:
      - "Preferencia por clientes premium"
      - "Minimizar CO2"
