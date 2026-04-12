# ... (cabecera de app.py)
st.sidebar.header("📊 Datos de la Vivienda")

# Campo para el enlace de Catastro
url_catastro = "https://catastro.navarra.es/ref_catastral/unidades.aspx?C=220&PO=7&PA=1097&lang=es"

# Botón para que el agente busque
if st.sidebar.button("🔍 Consultar Catastro (Tracasa)"):
    agente_temporal = AgenteNavarra({})
    m2_real = agente_temporal.obtener_superficie_catastro(url_catastro)
    st.session_state['m2'] = m2_real
    st.sidebar.success(f"Detectados {m2_real} m2")

# Usar el valor detectado o el manual
m2 = st.sidebar.number_input("Superficie útil (m2)", 
                             value=st.session_state.get('m2', 110.0))
# ... (resto del código de app.py igual)
