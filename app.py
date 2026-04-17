# ... (resto del código igual) ...

with col_tec:
    st.subheader("📋 Detalles Técnicos")
    for item in desglose_detallado:
        st.write(f"✅ **{item['nombre']}**")
        st.caption(f"Concepto: {item['razon']}")
        st.write(f"Monto: **{item['monto']:,.2f}€**")
        if 'fecha_limite' in item:
            st.warning(f"⏳ Plazo hasta: {item['fecha_limite']}")
        st.markdown("---")

# ... (resto del código igual) ...
