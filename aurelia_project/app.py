import streamlit as st
import yaml
from pathlib import Path
 
from modules.model_representation import ProblemSpec
from modules.model_ml import predict_demand
from modules.model_or import Package, greedy_select
from modules.model_hybrid import traffic_from_rain, plan_route_8h
 
st.set_page_config(page_title="Aurelia Decision Cockpit", layout="wide")
 
 
@st.cache_data
def load_catalog(path: str):
    p = Path(path)
    if not p.exists():
        return {"cases": []}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {"cases": []}
 
 
def init_state():
    st.session_state.setdefault("problem_spec", None)
    st.session_state.setdefault("ml_prediction", None)
    st.session_state.setdefault("ml_inputs", None)
    st.session_state.setdefault("or_solution", None)
    st.session_state.setdefault("hybrid_plan", None)
 
 
def page_home():
    st.title("Cockpit de Decisiones - Aurelia Retail")
    st.write(
        "Simulador educativo para decisiones de logística de última milla.\n\n"
        "Idea clave: la IA **reduce incertidumbre** (predicción) y la OR **gestiona complejidad** (optimización)."
    )
 
 
def page_representation(catalog):
    st.header("Módulo 1 — Diseñador de Problemas (S/A/T/G/C/R)")
 
    cases = catalog.get("cases", [])
    case_names = ["(sin plantilla)"] + [c.get("name", c.get("id", "case")) for c in cases]
    chosen = st.selectbox("Plantilla (cases/catalog.yml)", case_names, index=0)
 
    preset = None
    if chosen != "(sin plantilla)":
        preset = next((c for c in cases if c.get("name") == chosen or c.get("id") == chosen), None)
 
    S = st.text_area("S (Estado)", value=(preset.get("S") if preset else ""), height=100)
    A = st.text_area("A (Acciones)", value=(preset.get("A") if preset else ""), height=100)
    T = st.text_area("T (Transiciones)", value=(preset.get("T") if preset else ""), height=100)
    G = st.text_area("G (Objetivos)", value=(preset.get("G") if preset else ""), height=100)
    C = st.text_area("C (Restricciones - texto libre)", value=(preset.get("C") if preset else ""), height=100)
    R = st.text_area("R (Riesgos/Recompensa/Resultado)", value=(preset.get("R") if preset else ""), height=100)
 
    st.subheader("Clasifica restricciones (Hard vs Soft)")
    hard_opts = (preset.get("hard_constraints") if preset else []) or ["Capacidad del camión", "Ventana horaria", "Normativa"]
    soft_opts = (preset.get("soft_constraints") if preset else []) or ["Preferencias de cliente", "Equidad", "Minimizar CO2"]
 
    hard_selected = [x for x in hard_opts if st.checkbox(f"[Hard] {x}", value=True, key=f"hard_{x}")]
    soft_selected = [x for x in soft_opts if st.checkbox(f"[Soft] {x}", value=False, key=f"soft_{x}")]
 
    if st.button("Generar Ficha"):
        spec = ProblemSpec(S=S, A=A, T=T, G=G, C=C, R=R, hard_constraints=hard_selected, soft_constraints=soft_selected)
        st.session_state["problem_spec"] = spec
        st.success("Ficha generada y guardada en sesión.")
 
    spec = st.session_state.get("problem_spec")
    if spec:
        st.markdown(spec.to_markdown())
 
 
def page_ml():
    st.header("Módulo 2 — Predictor (ML supervisado simulado)")
 
    col1, col2, col3 = st.columns(3)
    with col1:
        dow = st.slider("Día de la semana (0=Lun, 6=Dom)", 0, 6, 0)
    with col2:
        rain = st.slider("Lluvia (0=sol, 1=lluvia)", 0.0, 1.0, 0.3, 0.05)
    with col3:
        promo = st.toggle("Promoción activa", value=False)
 
    if st.button("Predecir Demanda"):
        pred = predict_demand(day_of_week=dow, rain=rain, promo=promo)
        st.session_state["ml_prediction"] = pred
        st.session_state["ml_inputs"] = {"dow": dow, "rain": rain, "promo": promo}
        st.success("Predicción guardada en sesión.")
 
    pred = st.session_state.get("ml_prediction")
    if pred:
        st.metric("Demanda estimada (paquetes)", f"{pred.demand:.0f}")
        st.caption("Nota: esto es **predicción (info)**, no **decisión (acción)**.")
        with st.expander("Detalles del cálculo"):
            st.write(pred)
 
 
def page_or():
    st.header("Módulo 3 — Optimizador (OR) — Greedy knapsack")
 
    capacity = st.number_input("Capacidad del camión (peso)", min_value=0.0, value=50.0, step=1.0)
 
    st.subheader("Paquetes (peso, valor)")
    pkgs = []
    for i in range(1, 7):
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            pid = st.text_input(f"ID {i}", value=chr(64 + i), key=f"pid_{i}")
        with c2:
            w = st.number_input(f"Peso {i}", min_value=0.0, value=float(5 * i), step=1.0, key=f"w_{i}")
        with c3:
            v = st.number_input(f"Valor {i}", min_value=0.0, value=float(10 * i), step=1.0, key=f"v_{i}")
        pkgs.append(Package(pkg_id=pid, weight=w, value=v))
 
    mode = st.selectbox("Criterio greedy", ["value", "ratio"], index=0)
 
    if st.button("Optimizar carga"):
        sol = greedy_select(capacity=capacity, packages=pkgs, mode=mode)
        st.session_state["or_solution"] = sol
        st.success("Solución OR guardada en sesión.")
 
    sol = st.session_state.get("or_solution")
    if sol:
        st.write("Seleccionados:", [p.pkg_id for p in sol.selected])
        st.write(f"Peso total: {sol.total_weight:.1f} / {capacity:.1f}")
        st.write(f"Valor total: {sol.total_value:.1f}")
        st.progress(sol.utilization)
 
 
def page_hybrid():
    st.header("Módulo 4 — Sistema híbrido (ML + OR)")
 
    pred = st.session_state.get("ml_prediction")
    ml_inputs = st.session_state.get("ml_inputs")
 
    if not pred or not ml_inputs:
        st.warning("Primero genera una predicción en el Módulo 2 (ML) para alimentar el híbrido.")
        return
 
    st.info("Conectamos lluvia → tráfico → paradas máximas en 8h (comparativa estático vs con ML).")
 
    rain = float(ml_inputs["rain"])
    risk = st.selectbox("Nivel de riesgo", ["Conservador", "Neutro", "Agresivo"], index=1)
 
    traffic_ml = traffic_from_rain(rain)
 
    static_plan = plan_route_8h(traffic_minutes=8.0, risk_level=risk)     # baseline fijo
    ml_plan = plan_route_8h(traffic_minutes=traffic_ml, risk_level=risk)  # ajustado por lluvia
 
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Planificación Estática")
        st.write(f"Min/stop: {static_plan.minutes_per_stop:.1f}")
        st.write(f"Stops máx (8h): {static_plan.max_stops}")
 
    with c2:
        st.subheader("Planificación con ML")
        st.write(f"Min/stop: {ml_plan.minutes_per_stop:.1f}")
        st.write(f"Stops máx (8h): {ml_plan.max_stops}")
 
    st.session_state["hybrid_plan"] = {"static": static_plan, "ml": ml_plan}
    st.caption("Intuición: más lluvia → más tráfico → menos paradas factibles → plan más conservador.")
 
 
def page_copilot():
    st.header("Módulo 5 — Copiloto (LLM) — Auditoría simulada")
 
    spec = st.session_state.get("problem_spec")
    if not spec:
        st.warning("Primero define el problema en el Módulo 1 para poder auditarlo.")
        return
 
    prompt = f"""
Eres un auditor de modelos de decisión. Revisa esta especificación y sugiere mejoras:
- S: {spec.S}
- A: {spec.A}
- T: {spec.T}
- G: {spec.G}
- C: {spec.C}
- Hard: {spec.hard_constraints}
- Soft: {spec.soft_constraints}
- R: {spec.R}
 
Devuelve:
1) Ambigüedades detectadas
2) Restricciones faltantes probables
3) Riesgos legales/operativos
4) Métricas recomendadas
""".strip()
 
    if st.button("Auditar mi modelo"):
        st.subheader("Prompt plantilla (mostrado)")
        st.code(prompt, language="text")
 
        findings = []
        if len(spec.hard_constraints) == 0:
            findings.append("- No hay hard constraints marcadas; el optimizador puede ser irrealista.")
        if "ventana" not in (spec.C or "").lower():
            findings.append("- Falta explicitar ventanas horarias / SLA si aplica a última milla.")
        if "norma" not in (spec.C or "").lower() and "legal" not in (spec.R or "").lower():
            findings.append("- Riesgo: no se menciona cumplimiento normativo (tráfico/zonas/privacidad).")
 
        st.subheader("Auditoría simulada (respuesta ejemplo)")
        st.write("**Ambigüedades / faltantes**")
        st.write("\n".join(findings) if findings else "- No se detectan faltantes obvios con estas heurísticas.")
        st.write("**Métricas recomendadas**")
        st.write("- % entregas a tiempo, coste por entrega, utilización de capacidad, incidencias, quejas, CO2 estimado.")
        st.caption("Nota: el copiloto documenta/audita; no toma decisiones operativas.")
 
 
def main():
    init_state()
    catalog = load_catalog("cases/catalog.yml")
 
    pages = [
        st.Page(page_home, title="Inicio", icon="🏁"),
        st.Page(lambda: page_representation(catalog), title="1) Representación", icon="🧩"),
        st.Page(page_ml, title="2) ML Predictor", icon="📈"),
        st.Page(page_or, title="3) OR Optimizer", icon="🧮"),
        st.Page(page_hybrid, title="4) Híbrido", icon="🔀"),
        st.Page(page_copilot, title="5) Copiloto", icon="🕵️"),
    ]
    nav = st.navigation(pages)
    nav.run()
 
 
if __name__ == "__main__":
    main()
