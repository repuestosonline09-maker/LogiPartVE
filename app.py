import streamlit as st
import google.generativeai as genai
import re

# Configuración de la página
st.set_page_config(page_title="Cotizador Logístico", layout="wide")

# Estilos CSS
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; background-color: #007bff; color: white; }
    .card-aereo { padding: 20px; border-radius: 10px; background-color: #e3f2fd; border-left: 5px solid #1976d2; }
    .card-maritimo { padding: 20px; border-radius: 10px; background-color: #e8f5e9; border-left: 5px solid #388e3c; }
    </style>
""", unsafe_allow_html=True)
# Sidebar para configuración
with st.sidebar:
    st.header("⚙️ Configuración")
    admin_pass = st.text_input("Contraseña Admin", type="password")
    if admin_pass == "admin123":
        api_key = st.text_input("Google API Key", type="password")
        if api_key:
            genai.configure(api_key=api_key)
            st.success("API Conectada")

st.title("📦 Cotizador de Repuestos Internacional")

# Formulario principal
col1, col2, col3 = st.columns(3)
with col1:
    vehiculo = st.text_input("Vehículo (Año/Marca/Modelo)", placeholder="Ej: 1985 Ford Granada")
with col2:
    repuesto = st.text_input("Nombre del Repuesto", placeholder="Ej: Motor de arranque")
with col3:
    nro_parte = st.text_input("N° de Parte (Opcional)", placeholder="Ej: 3361031")

if st.button("COTIZAR AHORA"):
    if not api_key:
        st.error("Por favor, ingresa la API Key en el panel lateral.")
    else:
        try:
            # Configuración de seguridad y modelo
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            
            model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings)
            
            prompt = f"""
            Analiza el repuesto para: {vehiculo}, Pieza: {repuesto}, N°: {nro_parte}.
            Responde ÚNICAMENTE en este formato exacto:
            ANÁLISIS: (Descripción técnica)
            PESO_ESTIMADO: (Número)
            PRECIO_REPUESTO: (Número)
            AÉREO_COSTO: (Número)
            AÉREO_DIAS: (Días)
            MARÍTIMO_COSTO: (Número)
            MARÍTIMO_DIAS: (Días)
            ADUANA: (Porcentaje)
            """
            
            response = model.generate_content(prompt)
            texto = response.text
            
            # Extraer datos con Regex
            def extraer(patron, texto):
                resultado = re.search(patron, texto)
                return resultado.group(1) if resultado else "N/A"

            # Mostrar resultados en tarjetas
            st.info(f"🔍 **Análisis Técnico:** {extraer(r'ANÁLISIS: (.*)', texto)}")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                <div class="card-aereo">
                    <h3>✈️ Envío Aéreo</h3>
                    <p><b>Costo Total:</b> ${extraer(r'AÉREO_COSTO: (.*)', texto)} USD</p>
                    <p><b>Tiempo:</b> {extraer(r'AÉREO_DIAS: (.*)', texto)}</p>
                    <small>Peso est: {extraer(r'PESO_ESTIMADO: (.*)', texto)} lb</small>
                </div>
                """, unsafe_allow_html=True)
                
            with c2:
                st.markdown(f"""
                <div class="card-maritimo">
                    <h3>🚢 Envío Marítimo</h3>
                    <p><b>Costo Total:</b> ${extraer(r'MARÍTIMO_COSTO: (.*)', texto)} USD</p>
                    <p><b>Tiempo:</b> {extraer(r'MARÍTIMO_DIAS: (.*)', texto)}</p>
                    <p><small>Aduana: {extraer(r'ADUANA: (.*)', texto)}</small></p>
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error de conexión: Verifica que tu API Key sea válida y no tenga restricciones regionales.")
            st.write(e)
