import streamlit as st
from agentes import AgenteNavarra

# Configuración de la interfaz
st.set_page_config(page_title="Visor Santacara", page_icon="🏡", layout="wide")

if 'm2' not in st.session_state:
    st.session_state['m2'] = 110.0

st.title("🏡 Santacara Sostenible: Plan de Rehabilitación")
st.markdown("---")

# --- BARRA LATERAL ---
st.sidebar.header("🔍 Datos de Catastro")
muni = st.sidebar.text_input("Municipio", "220")
pol = st.sidebar.text_input("Polígono", "7")
par = st.sidebar.text_input("Parcela", "1097")

if st.sidebar.button("Consultar Catastro"):
    ag_temp = AgenteNavarra({"letra_actual": "E", "letra_objetivo": "A", "placas": True})
    st.session_state['m2'] = ag_temp.obtener_superficie_catastro(muni, pol, par)

m2_f = st.sidebar.number_input("Superficie (m2)", value=float(st.session_state['m2']))
l_act = st.sidebar.selectbox("Eficiencia Actual", ["G", "F", "E", "D"], index=2)
l_obj = st.sidebar.selectbox("Eficiencia Objetivo", ["A", "B", "C"], index=0)
placas = st.sidebar.checkbox("¿Incluir Fotovoltaica?", value=True)

# --- CÁLCULOS ---
agente = AgenteNavarra({"letra_actual": l_act, "letra_objetivo": l_obj, "placas": placas})
p_ref = agente.obtener_precio_referencia()
presupuesto = float(m2_f) * p_ref
ayuda, desglose = agente.calcular_subvenciones(presupuesto)
porc = (ayuda / presupuesto) * 100 if presupuesto > 0 else 0

# --- RESULTADOS FINANCIEROS ---
st.subheader("📊 Análisis Económico")
c1, c2, c3 = st.columns(3)
c1.metric("Inversión Bruta", f"{presupuesto:,.2f}€")
c2.metric("Subvención", f"{ayuda:,.2f}€", f"{porc:.1f}% cubierto")
c3.metric("Neto Vecino", f"{(presupuesto - ayuda):,.2f}€", delta_color="inverse")

st.progress(porc / 100)
st.markdown("---")

# --- INFORME IA Y DESGLOSE ---
col_ia, col_tec = st.columns([2, 1])

with col_ia:
    st.subheader("🤖 Informe del Consultor IA")
    if st.button("Generar Informe Institucional"):
        with st.spinner("Redactando informe con datos técnicos..."):
            texto = agente.explicar_con_ia(presupuesto, ayuda, desglose)
            st.markdown(texto)

with col_tec:
    st.subheader("📋 Trámites y Detalles")
    for d in desglose:
        st.write(f"**{d['nombre']}**")
        st.write(f"Cuantía: **{d['monto']:,.2f}€**")
        st.caption(f"Concepto: {d['razon']}")
        if 'fecha_limite' in d:
            st.warning(f"⏳ Límite: {d['fecha_limite']}")
        st.markdown("---")
