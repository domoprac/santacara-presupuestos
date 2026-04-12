import streamlit as st
from agentes import AgenteNavarra

# Configuración de la página
st.set_page_config(page_title="Santacara Sostenible", page_icon="🏡")

st.title("🏡 Rehabilitación Casa del Médico - Santacara")
st.markdown("---")

# --- SIDEBAR: VARIABLES TÉCNICAS (Entradas del usuario) ---
st.sidebar.header("📊 Datos de la Vivienda")
m2 = st.sidebar.number_input("Superficie útil (m2)", value=110)

st.sidebar.subheader("Certificación Energética")
letra_actual = st.sidebar.selectbox("Letra Actual", ["G", "F", "E", "D", "C"], index=2)
letra_objetivo = st.sidebar.selectbox("Letra tras Reforma", ["A", "B", "C"], index=0)

st.sidebar.subheader("Sistemas a Instalar")
tiene_placas = st.sidebar.checkbox("Fotovoltaica + Baterías", value=True)
tiene_clima = st.sidebar.checkbox("Suelo Radiante Eléctrico + ACS", value=True)

# --- EJECUCIÓN DEL AGENTE (Lógica y Conexión) ---
# 1. Preparamos los datos para el agente
datos_vivienda = {
    "municipio": "Santacara",
    "poblacion_menor_5000": True,
    "letra_actual": letra_actual,
    "letra_objetivo": letra_objetivo,
    "placas": tiene_placas
}

# 2. Inicializamos el agente
agente = AgenteNavarra(datos_vivienda)

# 3. El agente obtiene el precio de referencia (desde el repo de Domoprac o por defecto)
precio_m2_real = agente.obtener_precio_referencia()

# 4. Cálculo del presupuesto bruto basado en el dato del agente
presupuesto_obra = m2 * precio_m2_real

# 5. El agente calcula las subvenciones aplicables en Navarra
ahorro_total, detalles = agente.calcular_subvenciones(presupuesto_obra)

# 6. Resultado final
coste_final = presupuesto_obra - ahorro_total

# --- INTERFAZ DE RESULTADOS (Lo que ve el usuario) ---
col1, col2 = st.columns(2)
with col1:
    st.metric("Inversión Bruta", f"{presupuesto_obra:,.2f}€")
    st.caption(f"Precio m² aplicado: {precio_m2_real:,.2f}€ (vía Repo/Agente)")

with col2:
    st.metric("Coste Neto Ayuntamiento", f"{coste_final:,.2f}€", 
              delta=f"-{ahorro_total:,.2f}€ Subvencionado", delta_color="normal")

st.write("### 📝 Desglose del Agente de Subvenciones")
for d in detalles:
    st.info(f"**{d['nombre']}**: {d['monto']:,.2f}€ ({d['razon']})")

# Alerta de éxito si hay un buen salto de eficiencia
if letra_actual > "D" and letra_objetivo <= "B":
    st.success("✅ **Bonus detectado:** El salto de letra energética cumple los requisitos para la ayuda máxima en Navarra.")

st.markdown("---")
st.caption("Esta herramienta utiliza agentes para validar precios del repositorio Domoprac y normativas del BON.")