import streamlit as st
from agentes import AgenteNavarra

# Configuración de página
st.set_page_config(page_title="Santacara Sostenible", page_icon="🏡", layout="wide")

if 'm2' not in st.session_state:
    st.session_state['m2'] = 110.0

st.title("🏡 Santacara Sostenible: Rehabilitación y Autoconsumo")
st.markdown("---")

# --- SIDEBAR ---
st.sidebar.header("🔍 Localización Catastral")
muni = st.sidebar.text_input("Municipio", "220")
pol = st.sidebar.text_input("Polígono", "7")
par = st.sidebar.text_input("Parcela", "1097")

if st.sidebar.button("Consultar Catastro"):
    with st.spinner("Conectando con Tracasa..."):
        agente_temp = AgenteNavarra({"letra_actual": "E", "letra_objetivo": "A", "placas": True})
        st.session_state['m2'] = agente_temp.obtener_superficie_catastro(muni, pol, par)

st.sidebar.markdown("---")
st.sidebar.header("🛠️ Configuración Vivienda")
m2_f = st.sidebar.number_input("Metros m2", value=float(st.session_state['m2']))
l_act = st.sidebar.selectbox("Letra Actual", ["G", "F", "E", "D"], index=2)
l_obj = st.sidebar.selectbox("Letra Objetivo", ["A", "B", "C"], index=0)
placas = st.sidebar.checkbox("¿Instalar Placas Solares?", value=True)

# --- CÁLCULOS ---
datos_obra = {"letra_actual": l_act, "letra_objetivo": l_obj, "placas": placas}
agente = AgenteNavarra(datos_obra)

precio_ref = agente.obtener_precio_referencia()
presupuesto = float(m2_f) * precio_ref
ayuda_concedida, desglose = agente.calcular_subvenciones(presupuesto)
porcentaje = (ayuda_concedida / presupuesto) * 100 if presupuesto > 0 else 0

# --- RESULTADOS VISUALES ---
st.subheader("📊 Resumen Financiero")
c1, c2, c3 = st.columns(3)

c1.metric("Inversión Bruta", f"{presupuesto:,.2f}€")
c2.metric("Subvención Total", f"{ayuda_concedida:,.2f}€", f"{porcentaje:.1f}% cubierto")
c3.metric("Coste Neto Vecino", f"{(presupuesto - ayuda_concedida):,.2f}€", delta_color="inverse")

st.write(f"**Nivel de cobertura de ayudas:** {porcentaje:.1f}%")
st.progress(porcentaje / 100)
st.markdown("---")

# --- IA E INFORME ---
col_ia, col_tec = st.columns([2, 1])

with col_ia:
    st.subheader("🤖 Informe del Consultor IA")
    if st.button("Generar Informe Detallado"):
        with st.spinner("Analizando trámites y plazos..."):
            informe = agente.explicar_con_ia(presupuesto, ayuda_concedida, desglose)
            st.markdown(informe)

with col_tec:
    st.subheader("📋 Desglose Técnico")
    for d in desglose:
        st.write(f"🔹 **{d['nombre']}**")
        st.write(f"Monto: **{d['monto']:,.2f}€**")
        st.caption(f"Concepto: {d['razon']}")
        if 'fecha_limite' in d:
            st.error(f"⚠️ Plazo: {d['fecha_limite']}")
        st.markdown("---")
