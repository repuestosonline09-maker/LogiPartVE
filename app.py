import streamlit as st
import google.generativeai as genai
import re

# 1. Configuración de pantalla
st.set_page_config(page_title="LogiParts AI", layout="wide")

# 2. Estilos visuales
st.markdown("""
    <style>
    .card-aereo { padding: 20px; border-radius: 10px; background-color: #e3f2fd; border-left: 5px solid #1976d2; color: #1565c0; }
    .card-maritimo { padding: 20px; border-radius: 10px; background-color: #e8f5e9; border-left: 5px solid #388e3c; color: #2e7d32; }
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar y Conexión (Usa tu llave de Colombia aquí)
with st.sidebar:
    st.header("⚙️ Configuración")
    admin_pass = st.text_input("Contraseña Admin", type="password")
    api_key = ""
    if admin_pass == "admin123":
        api_key = st.text_input("Google API Key (Colombia)", type="password")
        if api_key:
            # Forzamos transporte REST para evitar el error 404 de v1beta
            genai.configure(api_key=api_key, transport='rest')
            st.success("✅ Conexión Exitosa")

st.title("📦 Cotizador Inteligente LogiParts")

# 4. Formulario
col1, col2, col3 = st.columns(3)
with col1:
    vehiculo = st.text_input("Vehículo", placeholder="Ej: 1985 Ford Granada")
with col2:
    repuesto = st.text_input("Pieza", placeholder="Ej: Motor de arranque")
with col3:
    nro_parte = st.text_input("N° Parte", placeholder="Ej: 3361031")

# 5. Lógica de Cotización
if st.button("COTIZAR AHORA"):
    if not api_key:
        st.error("⚠️ Ingresa la API Key en el panel lateral")
    else:
        try:
            # Usamos el nombre del modelo más estable
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            prompt = f"""
            Analiza: {vehiculo}, Pieza: {repuesto}, N°: {nro_parte}.
            Responde ÚNICAMENTE en este formato:
            ANÁLISIS: (Breve descripción técnica)
            PESO_ESTIMADO: (Número en lb)
            PRECIO_REPUESTO: (Número en USD)
            AÉREO_COSTO: (Número en USD)
            AÉREO_DIAS: (Días)
            MARÍTIMO_COSTO: (Número en USD)
            MARÍTIMO_DIAS: (Días)
            ADUANA: (Porcentaje)
            """
            
            response = model.generate_content(prompt)
            res_text = response.text
            
            # Función para extraer datos
            def buscar(tag, texto):
                match = re.search(f"{tag}: (.*)", texto)
                return match.group(1) if match else "N/D"

            st.info(f"🔍 **Análisis:** {buscar('ANÁLISIS', res_text)}")
            
            ca, cm = st.columns(2)
            with ca:
                st.markdown(f"""<div class="card-aereo"><h3>✈️ Aéreo</h3>
                <p><b>Total:</b> ${buscar('AÉREO_COSTO', res_text)}</p>
                <p><b>Tiempo:</b> {buscar('AÉREO_DIAS', res_text)}</p>
                <small>Peso: {buscar('PESO_ESTIMADO', res_text)}</small></div>""", unsafe_allow_html=True)
            with cm:
                st.markdown(f"""<div class="card-maritimo"><h3>🚢 Marítimo</h3>
                <p><b>Total:</b> ${buscar('MARÍTIMO_COSTO', res_text)}</p>
                <p><b>Tiempo:</b> {buscar('MARÍTIMO_DIAS', res_text)}</p>
                <small>Impuesto: {buscar('ADUANA', res_text)}</small></div>""", unsafe_allow_html=True)
            
            st.balloons()

        except Exception as e:
            st.error(f"Error de sistema: {e}")
