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

# 2. Sidebar
with st.sidebar:
    st.header("⚙️ Configuración")
    admin_pass = st.text_input("Contraseña Admin", type="password")
    api_key = ""
    if admin_pass == "admin123":
        api_key = st.text_input("Pega tu API Key", type="password")
        if api_key:
            st.success("✅ API Key detectada")

st.title("📦 Cotizador Inteligente LogiParts")

# 3. Formulario
col1, col2, col3 = st.columns(3)
with col1:
    vehiculo = st.text_input("🚙 Vehículo", placeholder="Ej: Toyota Hilux 2022")
with col2:
    repuesto = st.text_input("🔧 Pieza", placeholder="Ej: Amortiguadores")
with col3:
    nro_parte = st.text_input("🏷️ N° Parte", placeholder="Opcional")

# 4. Lógica de conexión
if st.button("GENERAR COTIZACIÓN AHORA"):
    if not api_key:
        st.error("⚠️ Ingresa la API Key en el panel lateral.")
    elif not vehiculo or not repuesto:
        st.warning("⚠️ Los campos Vehículo y Pieza son obligatorios.")
    else:
        try:
            # USAMOS V1BETA Y EL MODELO FLASH ESTÁNDAR (Alias más compatible)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"Eres un experto en logística. Crea una cotización para enviar a Venezuela: Vehículo {vehiculo}, Pieza {repuesto}, N° Parte {nro_parte}. Incluye peso estimado, precio en USD y comparación Aéreo vs Marítimo."
                    }]
                }]
            }
            
            headers = {'Content-Type': 'application/json'}
            
            with st.spinner('⏳ Conectando con Google AI...'):
                response = requests.post(url, headers=headers, json=payload)
                resultado = response.json()
                
            if response.status_code == 200:
                texto_ia = resultado['candidates'][0]['content']['parts'][0]['text']
                st.markdown("---")
                st.markdown("### 📋 Resultado de la Cotización")
                st.markdown(f'<div class="report-container">{texto_ia}</div>', unsafe_allow_html=True)
                st.balloons()
            else:
                # Si falla, mostramos el error exacto para diagnosticar
                error_msg = resultado.get('error', {}).get('message', 'Error desconocido')
                st.error(f"Error de Google: {error_msg}")
                
                # RECURSO DE EMERGENCIA: Si el anterior falla, intentamos con el alias 'latest'
                st.info("Intentando conexión alternativa...")
                url_alt = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
                response_alt = requests.post(url_alt, headers=headers, json=payload)
                if response_alt.status_code == 200:
                    st.success("Conexión alternativa exitosa. Por favor, refresca la página.")
                
        except Exception as e:
            st.error(f"Error de red: {str(e)}")

st.markdown("---")
st.caption("LogiParts AI - v1.2 (Compatibilidad Forzada)")
