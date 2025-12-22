import streamlit as st
import requests
import json

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="LogiPartVE Pro", layout="wide", page_icon="✈️")

# Carga de Secretos
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASS_ADMIN = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("⚠️ Error: Configure 'Secrets' en Streamlit.")
    st.stop()

# ESTADOS DE SESIÓN
if 'resultado_ia' not in st.session_state: st.session_state.resultado_ia = ""
if 'count' not in st.session_state: st.session_state.count = 0
if 'tarifas' not in st.session_state: st.session_state.tarifas = {"mia_a": 9.0, "mia_m": 40.0, "mad": 20.0}

# 2. DISEÑO CSS
st.markdown("""
    <style>
    .report-container { 
        padding: 20px; border-radius: 10px; background-color: #ffffff; 
        border: 2px solid #007bff; font-size: 15px;
    }
    .manual-table { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #dee2e6; }
    </style>
""", unsafe_allow_html=True)

# 3. SIDEBAR (ADMIN)
with st.sidebar:
    check_pass = st.text_input("Contraseña Admin", type="password")
    if check_pass == PASS_ADMIN:
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo ($/lb)", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo ($/ft³)", value=st.session_state.tarifas["mia_m"])

# 4. FORMULARIO
st.title("LogiPartVE: Gestión Experta DDP")
col1, col2, col3 = st.columns(3)
with col1: v_in = st.text_input("Vehículo", key=f"v_{st.session_state.count}")
with col2: r_in = st.text_input("Repuesto", key=f"r_{st.session_state.count}")
with col3: n_in = st.text_input("N° Parte", key=f"n_{st.session_state.count}")

# 5. LÓGICA DE IA (URL CORRECTA PARA CRÉDITOS Y PAGO)
if st.button("🚀 GENERAR ANÁLISIS", type="primary"):
    if v_in and r_in and n_in:
        # Esta URL v1beta es la única que reconoce los créditos de "Free Trial Upgrade" que tienes activos
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{"parts": [{"text": f"Experto LogiPartVE. Analiza {r_in} parte {n_in} para {v_in}. Diciembre 2025."}]}]
        }

        with st.spinner('Validando créditos y procesando...'):
            try:
                res = requests.post(url, json=payload)
                if res.status_code == 200:
                    st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
                else:
                    st.error(f"Error {res.status_code}: Google requiere re-autenticar tu saldo. Intenta en 1 minuto.")
            except Exception as e:
                st.error(f"Error de conexión: {str(e)}")
    else:
        st.warning("Faltan datos.")

# 6. RESULTADOS
if st.session_state.resultado_ia:
    st.markdown(f'<div class="report-container">{st.session_state.resultado_ia}</div>', unsafe_allow_html=True)
    if st.button("🗑️ LIMPIAR"):
        st.session_state.count += 1
        st.session_state.resultado_ia = ""
        st.rerun()
