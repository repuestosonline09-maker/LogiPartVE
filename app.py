import streamlit as st
import google.generativeai as genai

# 1. Configuración visual
st.set_page_config(page_title="LogiParts AI", layout="wide")

st.markdown("""
    <style>
    .report-container { padding: 20px; border-radius: 10px; background-color: #ffffff; border: 1px solid #e0e0e0; }
    .stButton>button { width: 100%; background-color: #007bff; color: white; font-weight: bold; }
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
            # Forzamos la versión v1 para evitar errores 404
            genai.configure(api_key=api_key, transport='rest', client_options={'api_version': 'v1'})
            st.success("✅ Conectado a Google AI")

st.title("📦 Cotizador Inteligente LogiParts")

# 3. Formulario de entrada
col1, col2, col3 = st.columns(3)
with col1:
    vehiculo = st.text_input("Vehículo (Año/Marca/Modelo)")
with col2:
    repuesto = st.text_input("Nombre de la Pieza")
with col3:
    nro_parte = st.text_input("Número de Parte (Opcional)")

# 4. Lógica de procesamiento
if st.button("GENERAR COTIZACIÓN"):
    if not api_key:
        st.error("⚠️ Falta la API Key en el panel lateral.")
    elif not vehiculo or not repuesto:
        st.warning("⚠️ Completa los datos del vehículo y la pieza.")
    else:
        try:
            # Usamos el modelo flash que es el más rápido
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Como experto logístico, analiza:
            Vehículo: {vehiculo}
            Repuesto: {repuesto}
            N° Parte: {nro_parte if nro_parte else 'No especificado'}
            
            Proporciona:
            1. Descripción técnica.
            2. Peso estimado (lb) y Precio sugerido (USD).
            3. Tiempo y costo estimado de envío a Venezuela (Aéreo y Marítimo).
            """
            
            with st.spinner('Analizando con IA...'):
                response = model.generate_content(prompt)
                
            st.markdown("---")
            st.markdown("### 📊 Reporte Generado")
            st.markdown(f'<div class="report-container">{response.text}</div>', unsafe_allow_html=True)
            st.balloons()
            
        except Exception as e:
            st.error(f"Error de comunicación: {e}")
            st.info("Asegúrate de que la API Key sea la correcta y que la App tenga acceso a internet.")
