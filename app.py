import streamlit as st
from agentes import AgenteNavarra

# Configuración
st.set_page_config(page_title="Santacara Inteligente", page_icon="🤖", layout="wide")

st.title("🏡 Santacara Sostenible + Copiloto IA")
st.markdown("Cálculo de rehabilitaciones con soporte de Inteligencia Artificial local (Ollama).")
st.markdown("---")

# --- SIDEBAR: ENTRADA DE DATOS ---
st.sidebar.header("🔍 Localización en Catastro")
c_muni = st.sidebar.text_input("Cód. Municipio", "220")
c_pol = st.sidebar.text_input("Polígono", "7")
c_par = st.sidebar.text_input("Parcela", "1097")

if st.sidebar.button("🔍 Consultar Catastro"):
    with st.spinner("Accediendo a Tracasa..."):
        m2_cat = AgenteNavarra({}).obtener_superficie_catastro(c_muni, c_pol, c_par)
        st.session_state['m2_valor'] = m2_cat
        st.sidebar.success(f"Superficie detectada: {m2_cat} m2")

m2 = st.sidebar.number_input("Superficie (m2)", value=st.session_state.get('m2_valor', 110.0))
l_act = st.sidebar.selectbox("Certificación Actual", ["G", "F", "E", "D"], index=2)
l_obj = st.sidebar.selectbox("Objetivo tras reforma", ["A", "B", "C"], index=0)
placas = st.sidebar.checkbox("Incluir Placas Fotovoltaicas", value=True)

# --- PROCESAMIENTO ---
datos_vivienda = {"letra_actual": l_act, "letra_objetivo": l_obj, "placas": placas}
agente = AgenteNavarra(datos_vivienda)

# Obtener precios y calcular
precio_base = agente.obtener_precio_referencia()
presupuesto_total = m2 * precio_base
ayuda_total, desglose = agente.calcular_subvenciones(presupuesto_total)

# --- RESULTADOS VISUALES ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Inversión Bruta", f"{presupuesto_total:,.2f}€")
with col2:
    st.metric("Subvenciones", f"{ayuda_total:,.2f}€")
with col3:
    st.metric("Inversión Neta", f"{presupuesto_total - ayuda_total:,.2f}€", delta_color="normal")

st.markdown("---")

# --- SECCIÓN DE IA ---
st.subheader("🤖 Informe del Copiloto IA")
if st.button("Generar Explicación Inteligente"):
    with st.spinner("Llama 3.2 está analizando el proyecto..."):
        informe_ia = agente.explicar_con_ia(presupuesto_total, ayuda_total)
        st.write(informe_ia)

st.markdown("---")
st.write("### 📋 Detalles Técnicos de las Ayudas")
for item in desglose:
    st.info(f"**{item['nombre']}**: {item['monto']:,.2f}€  \n*{item['razon']}*")
