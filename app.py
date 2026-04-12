import streamlit as st
from agentes import AgenteNavarra

st.set_page_config(page_title="Santacara Sostenible", page_icon="🏡", layout="wide")

st.title("🏡 Buscador de Ayudas - Catastro de Navarra")
st.markdown("---")

# --- SIDEBAR: BUSCADOR REAL ---
st.sidebar.header("🔍 Identificación de la Finca")
st.sidebar.info("Introduce los códigos de Tracasa")

# Datos por defecto de la Casa del Médico
cod_muni = st.sidebar.text_input("Código Municipio (Santacara = 220)", value="220")
poligono = st.sidebar.text_input("Polígono", value="7")
parcela = st.sidebar.text_input("Parcela", value="1097")

if st.sidebar.button("🔍 Consultar Superficie"):
    with st.spinner("El Agente está accediendo a Tracasa..."):
        agente_temp = AgenteNavarra({})
        # Le pasamos los datos que has escrito en los cuadros
        m2_detectados = agente_temp.obtener_superficie_catastro(cod_muni, poligono, parcela)
        st.session_state['m2_app'] = m2_detectados
        st.sidebar.success(f"Detectados: {m2_detectados} m2")

# Valor final para el cálculo
m2 = st.sidebar.number_input("Metros cuadrados confirmados", value=st.session_state.get('m2_app', 110.0))

st.sidebar.subheader("Reforma prevista")
l_act = st.sidebar.selectbox("Eficiencia Actual", ["G", "F", "E", "D", "C"], index=2)
l_obj = st.sidebar.selectbox("Eficiencia Objetivo", ["A", "B", "C"], index=0)
placas = st.sidebar.checkbox("¿Instalará Placas?", value=True)

# --- CÁLCULOS ---
datos_obra = {"letra_actual": l_act, "letra_objetivo": l_obj, "placas": placas}
agente = AgenteNavarra(datos_obra)

precio_m2 = agente.obtener_precio_referencia()
total_obra = m2 * precio_m2
ayuda_total, desglose = agente.calcular_subvenciones(total_obra)

# --- RESULTADOS ---
c1, c2 = st.columns(2)
with c1:
    st.metric("Presupuesto de Obra", f"{total_obra:,.2f}€")
with c2:
    st.metric("Coste tras Subvenciones", f"{total_obra - ayuda_total:,.2f}€", delta=f"-{ayuda_total:,.2f}€")

st.write("### 📝 Desglose del Agente")
for d in desglose:
    st.info(f"**{d['nombre']}**: {d['monto']:,.2f}€ ({d['razon']})")
