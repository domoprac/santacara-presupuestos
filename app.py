import streamlit as st
from agentes import AgenteNavarra

st.set_page_config(page_title="Santacara Sostenible", page_icon="🏡")

st.title("🚀 Rehabilitación Sostenible: Casa del Médico")
st.subheader("Municipio: Santacara (Navarra)")

# Sidebar para ajustes técnicos
st.sidebar.header("Configuración de Obra")
m2 = st.sidebar.number_input("Metros cuadrados", value=110)
coste_m2 = st.sidebar.slider("Coste m2 construcción (Modular)", 800, 1500, 1100)

coste_total_bruto = m2 * coste_m2

# Datos para el Agente
datos_vivienda = {
    "municipio": "Santacara",
    "poblacion_menor_5000": True,
    "propiedad": "Municipal"
}

# Ejecutar Agente
agente = AgenteNavarra(datos_vivienda)
coste_final, desglose = agente.calcular_presupuesto_neto(coste_total_bruto)

# Visualización de resultados
col1, col2 = st.columns(2)
with col1:
    st.metric("Coste Bruto", f"{coste_total_bruto:,.2f}€")
with col2:
    st.metric("Coste Neto (Con Ayudas)", f"{coste_final:,.2f}€", delta=f"-{(coste_total_bruto-coste_final):,.2f}€")

st.write("### 📋 Desglose de Subvenciones Aplicadas")
for item in desglose:
    st.success(item)

st.info("💡 Este presupuesto se actualiza automáticamente según el repositorio de Domoprac y el BON.")