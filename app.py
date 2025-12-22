import streamlit as st
import requests
import json

# 1. Configuración de pantalla
st.set_page_config(page_title="LogiParts AI", layout="wide", page_icon="📦")

st.markdown("""
    <style>
    .report-container { 
        padding: 25px; 
        border-radius: 15px; 
        background-color: #f8f9fa; 
        border: 1px solid #dee2e6; 
        color: #1a1a1a;
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

# 2. Sidebar
with st.sidebar:
    st.header("⚙️ Configuración")
    admin_pass = st.text_input("Contraseña Admin", type="password")
    api_key = ""
    if admin_pass == "admin123":
        api_key = st.text_input("Pega tu API Key", type="password")

st.title("📦 Cotizador Inteligente LogiParts")

# 3. Formulario
col1, col2, col3 = st.columns(3)
with col1:
    vehiculo = st.text_input("🚙 Vehículo")
with col2:
    repuesto = st.text_input("🔧 Pieza")
with col3:
    nro_parte = st.text_input("🏷️ N° Parte")

# 4. Lógica corregida sin errores de sintaxis
if st.button("GENERAR COTIZACIÓN AHORA"):
    if not api_key:
        st.error("⚠️ Falta la API Key en el panel lateral.")
    elif not vehiculo or not repuesto:
        st.warning("⚠️ Completa Vehículo y Pieza.")
    else:
        try:
            # URL usando gemini-1.5-flash-8b que es el que tu llave permite
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-8b:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"Experto en logística: Cotiza para Venezuela. Vehículo: {vehiculo}, Pieza: {repuesto}, Nro: {nro_parte}. Incluye descripción, peso lb, precio USD y envío Aéreo vs Marítimo."
                    }]
                }]
            }
            
            headers = {'Content-Type': 'application/json'}
            
            with st.spinner('⏳ Consultando IA...'):
                response = requests.post(url, headers=headers, json=payload)
                resultado = response.json()
                
            if response.status_code == 200:
                texto_ia = resultado['candidates'][0]['content']['parts'][0]['text']
                st.markdown("### 📋 Resultado")
                st.markdown(f'<div class="report-container">{texto_ia}</div>', unsafe_allow_html=True)
                st.balloons()
            else:
                # Aquí estaba el error de sintaxis, ahora está corregido:
                error_info = resultado.get('error', {})
                mensaje = error_info.get('message', 'Error desconocido')
                st.error(f"Error de Google: {mensaje}")
                
        except Exception as e:
            st.error(f"Error de sistema: {str(e)}")
