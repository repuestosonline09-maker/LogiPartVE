import streamlit as st
import requests
import json

# 1. Configuración de pantalla
st.set_page_config(page_title="LogiParts AI", layout="wide", page_icon="📦")

st.markdown("""
    <style>
    .report-container { 
        padding: 25px; border-radius: 15px; background-color: #f8f9fa; 
        border: 1px solid #dee2e6; color: #1a1a1a; white-space: pre-wrap;
    }
    .stButton>button { 
        width: 100%; background-color: #007bff; color: white; 
        height: 3.5em; font-weight: bold; border-radius: 10px;
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

# 4. Lógica de Auto-Detección y Petición
if st.button("GENERAR COTIZACIÓN AHORA"):
    if not api_key:
        st.error("⚠️ Ingresa la API Key en el panel lateral.")
    else:
        try:
            with st.spinner('🔍 Detectando modelo compatible...'):
                # PASO 1: Listar modelos disponibles para TU clave
                list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                list_res = requests.get(list_url).json()
                
                modelos_validos = [
                    m['name'] for m in list_res.get('models', []) 
                    if 'generateContent' in m.get('supportedGenerationMethods', [])
                    and ('flash' in m['name'] or 'pro' in m['name'])
                ]

                if not modelos_validos:
                    st.error("No se encontraron modelos de generación disponibles para esta API Key.")
                    st.stop()
                
                # Usamos el primer modelo válido encontrado (ej: models/gemini-1.5-flash-8b)
                modelo_a_usar = modelos_validos[0]
                st.info(f"✅ Conectado mediante: {modelo_a_usar}")

            # PASO 2: Realizar la cotización
            url = f"https://generativelanguage.googleapis.com/v1beta/{modelo_a_usar}:generateContent?key={api_key}"
            
            payload = {
                "contents": [{"parts": [{"text": f"Experto en logística: Cotiza para Venezuela. Vehículo: {vehiculo}, Pieza: {repuesto}, Nro: {nro_parte}. Incluye descripción, peso lb, precio USD y envío Aéreo vs Marítimo."}]}]
            }
            
            with st.spinner('⏳ Generando presupuesto...'):
                response = requests.post(url, json=payload)
                resultado = response.json()
                
            if response.status_code == 200:
                texto_ia = resultado['candidates'][0]['content']['parts'][0]['text']
                st.markdown("### 📋 Resultado")
                st.markdown(f'<div class="report-container">{texto_ia}</div>', unsafe_allow_html=True)
                st.balloons()
            else:
                st.error(f"Error: {resultado.get('error', {}).get('message', 'Error desconocido')}")
                
        except Exception as e:
            st.error(f"Error de conexión: {str(e)}")

st.caption("LogiParts AI - Sistema Auto-Configurable")
