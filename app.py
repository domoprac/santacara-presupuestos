import streamlit as st
from agentes import AgenteNavarra

# 1. Configuración de la página - SIEMPRE DEBE SER LA PRIMERA LÍNEA DE STREAMLIT
st.set_page_config(page_title="Santacara Sostenible", page_icon="🏡")

st.title("🏡 Rehabilitación Casa del Médico - Santacara")
st.markdown("---")

# --- SIDEBAR: VARIABLES TÉCNICAS ---
st.sidebar.header("📊 Datos de la Vivienda")

# URL de Tracasa (Catastro)
url_catastro = "https://catastro.navarra.es/ref_catastral/unidades.aspx?C=220&PO=7&PA=1097&lang=es"

# Botón para que el Agente lea Tracasa
if st.sidebar.button("🔍 Consultar Catastro (Tracasa)"):
    # Agente temporal para los m2
    agente_busqueda = AgenteNavarra({})
    m2_detectados = agente_busqueda.obtener_superficie_catastro(url_catastro)
    st.session_state['m2_valor'] = m2_detectados
    st.sidebar.success(f"Catastro leído: {m2_detectados} m2")

# Definir el valor de m2
valor_inicial = st.session_state.get('m2_valor', 110.0)
m2 = st.sidebar.number_input("Superficie útil (m2)", value=valor_inicial)

st.sidebar.subheader("Certificación Energética")
letra_actual = st.sidebar.selectbox("Letra Actual", ["G", "F", "E", "D", "C"], index=2)
letra_objetivo = st.sidebar.selectbox("Letra tras Reforma", ["A", "B", "C"], index=0)

st.sidebar.subheader("Sistemas a Instalar")
tiene_placas = st.sidebar.checkbox("Fotovoltaica + Baterías", value=True)

# --- LÓGICA CON EL AGENTE ---
datos_vivienda = {
    "letra_actual": letra_actual,
    "letra_objetivo": letra_objetivo,
    "placas": tiene_placas
}

agente = AgenteNavarra(datos_vivienda)

# Obtener precio del repo de Domoprac
precio_m2_real = agente.obtener_precio_referencia()
presupuesto_obra = m2 * precio_m2_real

# Calcular subvenciones
ahorro_total, detalles = agente.calcular_subvenciones(presupuesto_obra)
coste_final = presupuesto_obra - ahorro_total

# --- INTERFAZ DE RESULTADOS ---
col1, col2 = st.columns(2)
with col1:
    st.metric("Inversión Bruta", f"{presupuesto_obra:,.2f}€")
    st.caption(f"Precio m²: {precio_m2_real:,.2f}€")

with col2:
    st.metric("Coste Neto Ayuntamiento", f"{coste_final:,.2f}€", 
              delta=f"-{ahorro_total:,.2f}€ Ayudas", delta_color="normal")

st.write("### 📝 Informe del Agente (Navarra)")
for d in detalles:
    st.info(f"**{d['nombre']}**: {d['monto']:,.2f}€ - {d['razon']}")

st.markdown("---")
st.caption("Conectado a Tracasa y Domoprac.")
