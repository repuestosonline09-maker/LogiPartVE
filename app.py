import streamlit as st
import requests
import json

# 1. Configuración de pantalla
st.set_page_config(page_title="LogiParts AI", layout="wide")

st.markdown("""
    <style>
    .report-container { padding: 20px; border-radius: 10px; background-color: #f8f9fa; border: 1px solid #dee2e6; line-height: 1.6; }
    .stButton>button { width: 100%; background-color: #007bff; color: white; height: 3em; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. Sidebar
with st.sidebar:
    st.header("⚙️ Configuración")
    admin_pass = st.text_input("Contraseña Admin", type="password")
    api_key = ""
    if admin_pass == "admin123":
        api_key = st.text_input("Pega tu API Key de Colombia", type="password")
        if api_key:
            st.success("✅ API Key lista")

st.title("📦 Cotizador Inteligente LogiParts")

# 3. Formulario
col1, col2, col3 = st.columns(3)
with col1:
    vehiculo = st.text_input("Vehículo (Año/Marca/Modelo)")
with col2:
    repuesto = st.text_input("Pieza")
with col3:
    nro_parte = st.text_input("N° Parte (Opcional)")

# 4. Conexión Directa por API REST (Sin librerías intermedias)
if st.button("GENERAR COTIZACIÓN"):
    if not api_key:
        st.error("⚠️ Falta la API Key")
    elif not vehiculo or not repuesto:
        st.warning("⚠️ Completa los datos")
    else:
        try:
            # Forzamos la URL de la versión 1 estable
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"Actúa como experto logístico. Analiza para Venezuela: Vehículo {vehiculo}, Pieza {repuesto}, N° Parte {nro_parte}. Da peso en lb, precio USD y costos envío Aéreo/Marítimo."
                    }]
                }]
            }
            
            headers = {'Content-Type': 'application/json'}
            
            with st.spinner('Conectando directamente con Google AI v1...'):
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                resultado = response.json()
                
            if response.status_code == 200:
                texto_ia = resultado['candidates'][0]['content']['parts'][0]['text']
                st.markdown("---")
                st.markdown("### 📊 Reporte Logístico Final")
                st.markdown(f'<div class="report-container">{texto_ia}</div>', unsafe_allow_html=True)
                st.balloons()
            else:
                st.error(f"Error de Google: {resultado.get('error', {}).get('message', 'Error desconocido')}")
                
        except Exception as e:
            st.error(f"Error de red: {e}")
