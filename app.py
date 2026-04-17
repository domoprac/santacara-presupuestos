import streamlit as st
from agentes import AgenteNavarra

# Configuración
st.set_page_config(page_title="Santacara Sostenible", page_icon="🏡", layout="wide")

if 'm2' not in st.session_state:
    st.session_state['m2'] = 110.0

st.title("🏡 Santacara Sostenible")
st.markdown("---")

# --- SIDEBAR ---
st.sidebar.header("🔍 Catastro")
muni = st.sidebar.text_input("Municipio", "220")
pol = st.sidebar.text_input("Polígono", "7")
par = st.sidebar.text_input("Parcela", "1097")

if st.sidebar.button("Consultar Catastro"):
    agente_temp = AgenteNavarra({"letra_actual": "E", "letra_objetivo": "A", "placas": True})
    st.session_state['m2'] = agente_temp.obtener_superficie_catastro(muni, pol, par)

m2_f = st.sidebar.number_input("Metros m2", value=float(st.session_state['m2']))
l_act = st.sidebar.selectbox("Letra Actual", ["G", "F", "E", "D"], index=2)
l_obj = st.sidebar.selectbox("Letra Objetivo", ["A", "B", "C"], index=0)
placas = st.sidebar.checkbox("¿Placas Solares?", value=True)

# --- CÁLCULOS ---
datos_obra = {"letra_actual": l_act, "letra_objetivo": l_obj, "placas": placas}
agente = AgenteNavarra(datos_obra)

p_ref = agente.obtener_precio_referencia()
presupuesto = float(m2_f) * p_ref
ayuda_concedida, desglose = agente.calcular_subvenciones(presupuesto)
porc = (ayuda_concedida / presupuesto) * 100 if presupuesto > 0 else 0

# --- RESULTADOS ---
st.subheader("📊 Resumen Financiero")
c1, c2, c3 = st.columns(3)
c1.metric("Inversión Bruta", f"{presupuesto:,.2f}€")
c2.metric("Subvención", f"{ayuda_concedida:,.2f}€", f"{porc:.1f}%")
c3.metric("Neto Vecino", f"{(presupuesto - ayuda_concedida):,.2f}€", delta_color="inverse")

st.progress(porc / 100)
st.markdown("---")

# --- IA ---
col_ia, col_tec = st.columns([2, 1])

with col_ia:
    st.subheader("🤖 Informe IA")
    if st.button("Generar Informe"):
        with st.spinner("Redactando..."):
            # Aquí pasamos exactamente los 3 argumentos que pide la función
            texto = agente.explicar_con_ia(presupuesto, ayuda_concedida, desglose)
            st.markdown(texto)

with col_tec:
    st.subheader("📋 Detalles")
    for d in desglose:
        st.write(f"**{d['nombre']}**")
        st.caption(f"{d['monto']:,.2f}€")
        if 'fecha_limite' in d:
            st.error(f"Plazo: {d['fecha_limite']}")
        st.markdown("---")
