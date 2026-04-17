import streamlit as st
from agentes import AgenteNavarra

st.set_page_config(page_title="Santacara IA", page_icon="🏡")

if 'm2' not in st.session_state:
    st.session_state['m2'] = 110.0

st.title("🏡 Santacara Sostenible")

# SIDEBAR
st.sidebar.header("🔍 Catastro")
muni = st.sidebar.text_input("Municipio", "220")
pol = st.sidebar.text_input("Polígono", "7")
par = st.sidebar.text_input("Parcela", "1097")

if st.sidebar.button("Consultar Metros"):
    agente_b = AgenteNavarra({})
    st.session_state['m2'] = agente_b.obtener_superficie_catastro(muni, pol, par)

m2_f = st.sidebar.number_input("Superficie m2", value=float(st.session_state['m2']))
l_act = st.sidebar.selectbox("Letra Actual", ["G", "F", "E", "D"], index=2)
l_obj = st.sidebar.selectbox("Letra Objetivo", ["A", "B", "C"], index=0)
placas = st.sidebar.checkbox("Placas Solares", value=True)

# CÁLCULOS
agente = AgenteNavarra({"letra_actual": l_act, "letra_objetivo": l_obj, "placas": placas})
p_base = agente.obtener_precio_referencia()
presupuesto = float(m2_f) * p_base
ayuda, detalles = agente.calcular_subvenciones(presupuesto)

# UI
c1, c2 = st.columns(2)
c1.metric("Presupuesto", f"{presupuesto:,.2f}€")
c2.metric("Neta", f"{(presupuesto - ayuda):,.2f}€")

if st.button("🤖 Generar Informe IA"):
    with st.spinner("Groq está pensando a toda velocidad..."):
        texto = agente.explicar_con_ia(presupuesto, ayuda)
        st.write(texto)
