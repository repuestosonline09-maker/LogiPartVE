import streamlit as st
import google.generativeai as genai

# 1. Configuración de pantalla
st.set_page_config(page_title="LogiParts AI", layout="wide")

# Estilos básicos
st.markdown("""
    <style>
    .report-container { padding: 20px; border-radius: 10px; background-color: #f8f9fa; border: 1px solid #dee2e6; }
    .stButton>button { width: 100%; background-color: #007bff; color: white; height: 3em; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. Sidebar para la API Key
with st.sidebar:
    st.header("⚙️ Configuración")
    admin_pass = st.text_input("Contraseña Admin", type="password")
    api_key = ""
    if admin_pass == "admin123":
        api_key = st.text_input("Pega tu API Key aquí", type="password")
        if api_key:
            # Configuración simplificada para evitar ValueError
            genai.configure(api_key=api_key, transport='rest')
            st.success("✅ API Conectada")

st.title("📦 Cotizador Inteligente LogiParts")

# 3. Formulario
col1, col2, col3 = st.columns(3)
with col1:
    vehiculo = st.text_input("Vehículo (Año/Marca/Modelo)")
with col2:
    repuesto = st.text_input("Pieza")
with col3:
    nro_parte = st.text_input("N° Parte (Opcional)")

# 4. Lógica
if st.button("GENERAR COTIZACIÓN"):
    if not api_key:
        st.error("⚠️ Ingresa la API Key en el panel lateral.")
    elif not vehiculo or not repuesto:
        st.warning("⚠️ Indica al menos el vehículo y la pieza.")
    else:
        try:
            # Forzamos la versión v1 directamente en el nombre del modelo
            # Esta es la forma más compatible de hacerlo
            model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
            
            prompt = f"""
            Actúa como experto logístico internacional. Para el repuesto: {repuesto} 
            del vehículo: {vehiculo} (N° Parte: {nro_parte if nro_parte else 'N/A'}):
            
            1. Proporciona un breve análisis técnico.
            2. Estima peso en libras (lb).
            3. Estima costos de envío a Venezuela (Aéreo y Marítimo).
            """
            
            with st.spinner('Consultando IA...'):
                response = model.generate_content(prompt)
                
            st.markdown("---")
            st.markdown("### 📊 Reporte Logístico")
            st.markdown(f'<div class="report-container">{response.text}</div>', unsafe_allow_html=True)
            st.balloons()
            
        except Exception as e:
            # Si da error 404, probamos con el nombre corto
            try:
                model_alt = genai.GenerativeModel('gemini-1.5-flash')
                response = model_alt.generate_content(prompt)
                st.markdown(f'<div class="report-container">{response.text}</div>', unsafe_allow_html=True)
            except Exception as e2:
                st.error(f"Error de conexión: {e2}")
