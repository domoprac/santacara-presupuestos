import streamlit as st
from agentes import AgenteNavarra

st.set_page_config(page_title="Santacara IA", page_icon="🤖")

st.title("🏡 Proyecto Santacara Sostenible")
st.markdown("---")

# Inicialización de estado para evitar errores de cálculo
if 'm2_valor' not in st.session_state:
    st.session_state['m2_valor'] = 110.0

# --- SIDEBAR ---
st.sidebar.header("🔍 Datos Catastro")
c_muni = st.sidebar.text_input("Municipio", "220")
c_pol = st.sidebar.text_input("Polígono", "7")
c_par = st.sidebar.text_input("Parcela", "1097")

if st.sidebar.button("Consultar Catastro"):
    with st.spinner("Conectando con Tracasa..."):
        agente_b = AgenteNavarra({})
        m2_detectados = agente_b.obtener_superficie_catastro(c_muni, c_pol, c_par)
        st.session_state['m2_valor'] = m2_detectados
        st.sidebar.success(f"Detectado: {m2_detectados} m2")

m2_final = st.sidebar.number_input("Metros m2", value=float(st.session_state['m2_valor']))

l_act = st.sidebar.selectbox("Certificado Actual", ["G", "F", "E", "D"], index=2)
l_obj = st.sidebar.selectbox("Certificado Objetivo", ["A", "B", "C"], index=0)
placas = st.sidebar.checkbox("Incluir Placas Solares", value=True)

# --- LÓGICA DE NEGOCIO ---
datos = {"letra_actual": l_act, "letra_objetivo": l_obj, "placas": placas}
agente = AgenteNavarra(datos)

precio_m2 = agente.obtener_precio_referencia()
presupuesto_total = float(m2_final) * precio_m2
ayuda_total, desglose = agente.calcular_subvenciones(presupuesto_total)

# --- PANEL DE RESULTADOS ---
col1, col2 = st.columns(2)
col1.metric("Presupuesto Obra", f"{presupuesto_total:,.2f}€")
col2.metric("Subvención Total", f"{ayuda_total:,.2f}€")

st.info(f"**Inversión Neta Final: {(presupuesto_total - ayuda_total):,.2f}€**")

st.markdown("---")

# --- BOTÓN DE IA ---
if st.button("🤖 Generar Explicación Inteligente"):
    if "AIza" in agente.api_key and "TU_API_KEY" not in agente.api_key:
        with st.spinner("La IA está analizando los datos..."):
            informe = agente.explicar_con_ia(presupuesto_total, ayuda_total)
            st.markdown("### 📝 Informe de la IA")
            st.write(informe)
    else:
        st.error("Por favor, introduce una API Key válida en agentes.py")

st.markdown("### 📋 Desglose de Ayudas")
for d in desglose:
    st.write(f"- **{d['nombre']}**: {d['monto']:,.2f}€ ({d['razon']})")
