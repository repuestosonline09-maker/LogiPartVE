import streamlit as st
import requests
import json

# 1. Configuración de pantalla y Estética
st.set_page_config(page_title="LogiParts AI", layout="wide")

st.markdown("""
    <style>
    .report-container { 
        padding: 25px; 
        border-radius: 15px; 
        background-color: #ffffff; 
        border: 1px solid #e0e0e0; 
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        color: #1a1a1a;
        white-space: pre-wrap;
    }
    .stButton>button { 
        width: 100%; 
        background-color: #007bff; 
        color: white; 
        height: 3.5em; 
        font-weight: bold;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Sidebar para Credenciales
with st.sidebar:
    st.header("⚙️ Configuración")
    admin_pass = st.text_input("Contraseña Admin", type="password")
    api_key = ""
    if admin_pass == "admin123":
        api_key = st.text_input("Pega aquí tu API Key", type="password")
        if api_key:
            st.success("✅ API Key preparada")

st.title("📦 Cotizador Inteligente LogiParts")
st.info("Utilizando Inteligencia Artificial para análisis logístico internacional.")

# 3. Formulario de Entrada
col1, col2, col3 = st.columns(3)
with col1:
    vehiculo = st.text_input("🚙 Vehículo", placeholder="Año, Marca, Modelo")
with col2:
    repuesto = st.text_input("🔧 Pieza", placeholder="Nombre del repuesto")
with col3:
    nro_parte = st.text_input("🏷️ N° Parte", placeholder="Opcional")

# 4. Conexión Directa mediante API REST
if st.button("GENERAR COTIZACIÓN AHORA"):
    if not api_key:
        st.error("⚠️ Por favor, ingresa la API Key en el panel lateral.")
    elif not vehiculo or not repuesto:
        st.warning("⚠️ Los campos Vehículo y Pieza son obligatorios.")
    else:
        try:
            # CAMBIO AQUÍ: Usamos la versión estable v1
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"Eres un experto en logística automotriz. Genera un presupuesto detallado para enviar a Venezuela: Vehículo: {vehiculo}, Repuesto: {repuesto}, Nro Parte: {nro_parte}. Incluye: 1. Análisis de la pieza. 2. Peso estimado en lb. 3. Precio estimado del repuesto en USD. 4. Comparativa de envío Aéreo (7-10 días) vs Marítimo (3-4 semanas). Usa un tono profesional y formato limpio."
                    }]
                }]
            }
            
            headers = {'Content-Type': 'application/json'}
            
            with st.spinner('⏳ Procesando datos con Google AI...'):
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                resultado = response.json()
                
            if response.status_code == 200:
                texto_ia = resultado['candidates'][0]['content']['parts'][0]['text']
                
                st.markdown("---")
                st.markdown("### 📋 Resultado de la Cotización")
                # Mostramos el resultado
                st.markdown(f'<div class="report-container">{texto_ia}</div>', unsafe_allow_html=True)
                st.balloons()
            else:
                msg_error = resultado.get('error', {}).get('message', 'Error desconocido')
                st.error(f"Error de Google: {msg_error}")
                # Si el error persiste, intentamos con un alias alternativo
                st.info("Sugerencia: Si el error persiste, asegúrate de que tu API Key tenga habilitado el modelo Gemini 1.5 Flash en Google AI Studio.")
                
        except Exception as e:
            st.error(f"Error de red o sistema: {e}")

st.markdown("---")
st.caption("LogiParts AI - Sistema de asistencia logística basado en Gemini 1.5 Flash.")
