import streamlit as st
import requests
import json

# 1. Configuración de página
st.set_page_config(page_title="LogiPartVE AI", layout="wide", page_icon="🚛")

if 'resultado_ia' not in st.session_state:
    st.session_state.resultado_ia = ""

# 2. Estética LogiPartVE
st.markdown("""
    <style>
    .report-container { 
        padding: 20px; border-radius: 12px; background-color: #ffffff; 
        border: 2px solid #007bff; color: #1a1a1a;
    }
    .stButton>button { border-radius: 8px; height: 3em; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar: Panel Administrativo
with st.sidebar:
    st.header("🔐 Admin LogiPartVE")
    admin_pass = st.text_input("Password", type="password")
    api_key, t_aereo_mia, t_mar_mia, t_mad = "", 9.0, 40.0, 20.0
    if admin_pass == "admin123":
        api_key = st.text_input("Google API Key", type="password")
        t_aereo_mia = st.number_input("MIA Aéreo ($/lb)", value=9.0)
        t_mar_mia = st.number_input("MIA Marítimo ($/ft³)", value=40.0)
        t_mad = st.number_input("MAD Aéreo ($/kg)", value=20.0)

# 4. Interfaz de Usuario
st.title("🚛 LogiPartVE AI: Cotizador Express")

col_in1, col_in2, col_in3 = st.columns([2, 2, 1])
with col_in1: vehiculo = st.text_input("🚙 Vehículo", placeholder="Año, Marca, Modelo")
with col_in2: repuesto = st.text_input("🔧 Repuesto")
with col_in3: origen = st.selectbox("📍 Origen", ["Miami", "Madrid"])

# 5. Lógica de Petición
c_btn1, c_btn2 = st.columns([4, 1])

with c_btn1:
    if st.button("🚀 GENERAR COTIZACIÓN RESUMIDA", type="primary"):
        if not api_key: st.error("⚠️ Falta API Key.")
        else:
            try:
                # Detección de modelo
                list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                modelos = [m['name'] for m in requests.get(list_url).json().get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
                url = f"https://generativelanguage.googleapis.com/v1beta/{modelos[0]}:generateContent?key={api_key}"

                prompt = f"""
                Actúa como experto logístico de LogiPartVE. 
                PROPORCIONA UNA COTIZACIÓN ULTRA-RESUMIDA PARA: {repuesto} / {vehiculo} (Origen: {origen}).
                
                REGLAS:
                1. MIAMI: Da costo Aéreo (${t_aereo_mia}/lb) y Marítimo (${t_mar_mia}/ft³).
                2. MADRID: Solo Aéreo (${t_mad}/kg).
                3. Usa pesos/medidas con empaque REFORZADO.
                
                ESTRUCTURA OBLIGATORIA (Corta y Directa):
                - FICHA: Peso y Medidas estimadas.
                - COSTOS: Cuadro comparativo final.
                - CUADRO DE RECOMENDACIONES Y ALERTAS: 
                  * Recomendación específica de embalaje para esta pieza.
                  * ALERTAS EN TIEMPO REAL: Analiza problemas actuales (clima en el Atlántico, huelgas, retrasos aduanales en Venezuela o congestión en {origen}) que puedan afectar el tiempo de entrega HOY.
                
                Si no sabes el peso, responde 'NO LO SÉ'.
                """

                with st.spinner('⏳ Analizando rutas y alertas globales...'):
                    response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                    st.session_state.resultado_ia = response.json()['candidates'][0]['content']['parts'][0]['text']
            except: st.error("Error de conexión.")

with c_btn2:
    if st.button("🗑️ LIMPIAR"):
        st.session_state.resultado_ia = ""
        st.rerun()

# 6. Despliegue
if st.session_state.resultado_ia:
    st.markdown("---")
    st.markdown(f'<div class="report-container">{st.session_state.resultado_ia}</div>', unsafe_allow_html=True)

st.divider()
st.caption("LogiPartVE AI - Info actualizada en tiempo real sobre rutas aéreas y marítimas.")
