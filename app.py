import streamlit as st
from agentes import AgenteNavarra

# Configuración inicial
st.set_page_config(page_title="Santacara Sostenible", page_icon="🏡", layout="wide")

st.title("🏡 Rehabilitación Casa del Médico - Santacara")
st.markdown("Esta herramienta conecta con el **Catastro de Navarra** y el repositorio de precios de **Domoprac**.")
st.markdown("---")

# --- SIDEBAR: DATOS Y BÚSQUEDA ---
st.sidebar.header("🔍 Localización Catastral")
ref_catastral = st.sidebar.text_input("Referencia Catastral (Ej: 220-7-1097)", value="220-7-1097")

# Construcción de la URL de Tracasa
url_tracasa = f"https://catastro.navarra.es/ref_catastral/unidades.aspx?C=220&PO=7&PA=1097&lang=es"

if st.sidebar.button("🔍 Consultar Tracasa"):
    with st.spinner("El Agente está consultando el Catastro..."):
        agente_prov = AgenteNavarra({})
        m2_catastro = agente_prov.obtener_superficie_catastro(url_tracasa)
        st.session_state['m2_actual'] = m2_catastro
        st.sidebar.success(f"¡Datos extraídos! Superficie: {m2_catastro} m2")

# Ajuste manual de m2
m2_final = st.sidebar.number_input("Superficie útil para cálculo (m2)", 
                                   value=st.session_state.get('m2_actual', 110.0))

st.sidebar.subheader("Eficiencia Energética")
l_actual = st.sidebar.selectbox("Letra Actual", ["G", "F", "E", "D", "C"], index=2)
l_objetivo = st.sidebar.selectbox("Letra tras Reforma", ["A", "B", "C"], index=0)
placas = st.sidebar.checkbox("Incluir Placas Fotovoltaicas", value=True)

# --- PROCESAMIENTO CON EL AGENTE ---
datos_vivienda = {
    "letra_actual": l_actual,
    "letra_objetivo": l_objetivo,
    "placas": placas
}

agente = AgenteNavarra(datos_vivienda)
precio_m2 = agente.obtener_precio_referencia()
presupuesto_total = m2_final * precio_m2

subvencion, desglose = agente.calcular_subvenciones(presupuesto_total)
coste_ayuntamiento = presupuesto_total - subvencion

# --- PANEL DE RESULTADOS ---
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Presupuesto Estimado", f"{presupuesto_total:,.2f}€")
with c2:
    st.metric("Total Subvenciones", f"-{subvencion:,.2f}€", delta_color="normal")
with c3:
    st.metric("Inversión Neta Final", f"{coste_ayuntamiento:,.2f}€")

st.write("### 📄 Informe Detallado del Agente")
for item in desglose:
    st.info(f"**{item['nombre']}**: {item['monto']:,.2f}€  \n*{item['razon']}*")

st.warning("⚠️ **Nota:** Los datos de superficie se obtienen por defecto de la unidad urbana seleccionada en Tracasa. Verifique la cédula parcelaria para datos exactos.")
