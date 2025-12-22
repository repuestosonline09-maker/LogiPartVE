import streamlit as st
import google.generativeai as genai

# 1. Configuración de pantalla
st.set_page_config(page_title="LogiParts AI", layout="wide")

# 2. Sidebar y Conexión
with st.sidebar:
    st.header("⚙️ Configuración")
    admin_pass = st.text_input("Contraseña Admin", type="password")
    api_key = ""
    if admin_pass == "admin123":
        api_key = st.text_input("Pega tu API Key de Colombia", type="password")
        if api_key:
            genai.configure(api_key=api_key)
            st.success("✅ API Conectada")

st.title("📦 Cotizador LogiParts AI")
st.markdown("---")

# 3. Formulario con la casilla faltante
col1, col2, col3 = st.columns(3)
with col1:
    vehiculo = st.text_input("Vehículo", placeholder="Ej: 1985 Ford Granada")
with col2:
    repuesto = st.text_input("Pieza", placeholder="Ej: Motor de arranque")
with col3:
    nro_parte = st.text_input("N° de Parte", placeholder="Ej: 3361031")

# 4. Lógica de Cotización
if st.button("COTIZAR AHORA"):
    if not api_key:
        st.error("⚠️ Por favor, ingresa la API Key en el panel lateral.")
    elif not vehiculo or not repuesto:
        st.warning("⚠️ Por favor, indica al menos el vehículo y la pieza.")
    else:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Incluimos el N° de Parte en la consulta a la IA
            prompt = f"""
            Actúa como experto en logística internacional de repuestos automotrices.
            Analiza el siguiente requerimiento:
            - Vehículo: {vehiculo}
            - Pieza: {repuesto}
            - Número de Parte: {nro_parte if nro_parte else 'No especificado'}

            Por favor, genera un reporte detallado que incluya:
            1. Análisis técnico del repuesto.
            2. Peso estimado en libras (lb).
            3. Costo estimado del repuesto en USD.
            4. Comparativa de envío a Venezuela (Aéreo vs Marítimo) incluyendo tiempos de entrega y costos aproximados de nacionalización.
            """
            
            with st.spinner('Consultando inteligencia logística...'):
                response = model.generate_content(prompt)
                
            st.markdown("### 📊 Reporte Logístico Detallado")
            st.markdown("---")
            st.write(response.text)
            st.balloons()

        except Exception as e:
            st.error(f"Detalle técnico: {e}")
