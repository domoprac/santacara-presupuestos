import streamlit as st
from agentes import AgenteNavarra

st.set_page_config(page_title="Santacara Sostenible", page_icon="🏡")

# Inicializar metros en memoria
if 'm2' not in st.session_state:
    st.session_state['m2'] = 110.0

st.title("🏡 Santacara Sostenible")

# --- SIDEBAR ---
st.sidebar.header("🔍 Catastro Navarra")
muni = st.sidebar.text_input("Municipio", "220")
pol = st.sidebar.text_input("Polígono", "7")
par = st.sidebar.text_input("Parcela", "1097")

if st.sidebar.button("Consultar Metros"):
    with st.spinner("Buscando en Tracasa..."):
        agente_b = AgenteNavarra({"letra_actual": "E", "letra_objetivo": "A"})
        m2_res = agente_b.obtener_superficie_catastro(muni, pol, par)
        st.session_state['m2'] = m2_res
        st.sidebar.success(f"Metros: {m2_res}")

m2_final = st.sidebar.number_input("Superficie m2", value=float(st.session_state['m2']))
l_act = st.sidebar.selectbox("Letra Actual", ["G", "F", "E", "D"], index=2)
l_obj = st.sidebar.selectbox("Letra Objetivo", ["A", "B", "C"], index=0)
placas = st.sidebar.checkbox("Placas Solares", value=True)

# --- CÁLCULOS ---
datos = {"letra_actual": l_act, "letra_objetivo": l_obj, "placas": placas}
agente = AgenteNavarra(datos)

precio_base = agente.obtener_precio_referencia()
presupuesto = float(m2_final) * precio_base
ayuda, detalles = agente.calcular_subvenciones(presupuesto)

# --- RESULTADOS ---
c1, c2 = st.columns(2)
c1.metric("Presupuesto", f"{presupuesto:,.2f}€")
c2.metric("Neta (Tras ayudas)", f"{(presupuesto - ayuda):,.2f}€")

st.markdown("---")

if st.button("🤖 Generar Informe IA"):
    with st.spinner("La IA está pensando..."):
        informe = agente.explicar_con_ia(presupuesto, ayuda)
        st.subheader("📝 Informe Estratégico")
        st.write(informe)

st.write("### 📊 Desglose de ayudas")
for d in detalles:
    st.info(f"{d['nombre']}: {d['monto']:,.2f}€")
