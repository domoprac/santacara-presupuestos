import streamlit as st
from agentes import AgenteNavarra

# Configuración de página
st.set_page_config(page_title="Santacara IA", page_icon="🏡", layout="wide")

# Inicializar metros en el estado de la sesión si no existen
if 'm2' not in st.session_state:
    st.session_state['m2'] = 110.0

st.title("🏡 Santacara Sostenible: Rehabilitación Energética")
st.markdown("---")

# --- SIDEBAR: ENTRADA DE DATOS ---
st.sidebar.header("🔍 Consulta de Catastro")
muni = st.sidebar.text_input("Código Municipio", "220")
pol = st.sidebar.text_input("Polígono", "7")
par = st.sidebar.text_input("Parcela", "1097")

if st.sidebar.button("Consultar Metros en Tracasa"):
    with st.spinner("Conectando con Catastro Navarra..."):
        # Instancia temporal para buscar datos
        agente_b = AgenteNavarra({"letra_actual": "E", "letra_objetivo": "A", "placas": True})
        res_m2 = agente_b.obtener_superficie_catastro(muni, pol, par)
        st.session_state['m2'] = res_m2
        st.sidebar.success(f"Superficie detectada: {res_m2} m2")

st.sidebar.markdown("---")
st.sidebar.header("🛠️ Configuración de Obra")
m2_f = st.sidebar.number_input("Metros cuadrados finales", value=float(st.session_state['m2']))
l_act = st.sidebar.selectbox("Certificado Actual", ["G", "F", "E", "D"], index=2)
l_obj = st.sidebar.selectbox("Certificado Objetivo", ["A", "B", "C"], index=0)
placas = st.sidebar.checkbox("Incluir Placas Solares (Bonus)", value=True)

# --- LÓGICA DE NEGOCIO (CÁLCULOS) ---
datos_obra = {"letra_actual": l_act, "letra_objetivo": l_obj, "placas": placas}
agente = AgenteNavarra(datos_obra)

# Obtenemos precio y calculamos
precio_m2_ref = agente.obtener_precio_referencia()
presupuesto_total = float(m2_f) * precio_m2_ref
ayuda_concedida, desglose_detallado = agente.calcular_subvenciones(presupuesto_total)
coste_neto_vecino = presupuesto_total - ayuda_concedida
porcentaje_ahorro = (ayuda_concedida / presupuesto_total) * 100 if presupuesto_total > 0 else 0

# --- PANEL VISUAL DE RESULTADOS ---
st.subheader("📊 Resumen Económico")

# Fila de métricas
c1, c2, c3 = st.columns(3)
c1.metric("Inversión Bruta", f"{presupuesto_total:,.2f}€")
c2.metric("Subvención Estimada", f"{ayuda_concedida:,.2f}€", f"{porcentaje_ahorro:.0f}% de ahorro")
c3.metric("Coste Real Vecino", f"{coste_neto_vecino:,.2f}€", "- Neto", delta_color="inverse")

# Barra de progreso de la ayuda
st.write(f"**Cobertura de la subvención:** {porcentaje_ahorro:.1f}%")
st.progress(porcentaje_ahorro / 100)

st.info(f"💡 **Nota:** Esta estimación se basa en un coste de referencia de {precio_m2_ref:,.0f}€/m2 para rehabilitación energética en Navarra.")

st.markdown("---")

# --- BLOQUE DE INTELIGENCIA ARTIFICIAL ---
col_ia, col_tec = st.columns([2, 1])

with col_ia:
    st.subheader("🤖 Informe del Consultor IA")
    if st.button("Generar Informe Estratégico (Groq)"):
        with st.spinner("La IA de Santacara está redactando..."):
            informe_texto = agente.explicar_con_ia(presupuesto_total, ayuda_concedida)
            st.markdown(informe_texto)

with col_tec:
    st.subheader("📋 Detalles Técnicos")
    for item in desglose_detallado:
        st.write(f"✅ **{item['nombre']}**")
        st.caption(f"{item['razon']}: {item['monto']:,.2f}€")
