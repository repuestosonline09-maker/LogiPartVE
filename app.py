import streamlit as st
import requests
import json
import time

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="LogiPartVE Pro", layout="wide", page_icon="✈️")

# Carga de Secretos
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASS_ADMIN = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("⚠️ Error: Configure 'Secrets' en Streamlit con GOOGLE_API_KEY y ADMIN_PASSWORD.")
    st.stop()

# ESTADOS DE SESIÓN
if 'resultado_ia' not in st.session_state: st.session_state.resultado_ia = ""
if 'count' not in st.session_state: st.session_state.count = 0
if 'tarifas' not in st.session_state: st.session_state.tarifas = {"mia_a": 9.0, "mia_m": 40.0, "mad": 20.0}

# 2. DISEÑO CSS
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    .report-container { 
        padding: 20px; border-radius: 10px; background-color: #ffffff; 
        border: 2px solid #007bff; font-size: 15px; line-height: 1.5; color: #1e1e1e;
    }
    .manual-table { background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-top: 15px; border: 1px solid #dee2e6; }
    .stButton>button {width: 100%; height: 3em; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# 3. SIDEBAR (ADMIN)
with st.sidebar:
    st.header("⚙️ Configuración")
    check_pass = st.text_input("Contraseña Admin", type="password")
    if check_pass == PASS_ADMIN:
        st.success("Acceso concedido")
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo ($/lb)", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo ($/ft³)", value=st.session_state.tarifas["mia_m"])
        st.session_state.tarifas["mad"] = st.number_input("MAD Aéreo ($/kg)", value=st.session_state.tarifas["mad"])
    else:
        st.info("Ingrese clave para editar tarifas.")

# 4. ENCABEZADO
c1, c2 = st.columns([1, 6])
with c1: st.image("https://cdn-icons-png.flaticon.com/512/2208/2208233.png", width=70) 
with c2: st.title("LogiPartVE: Gestión Experta DDP")

# 5. FORMULARIO
with st.container():
    col1, col2, col3, col4, col5 = st.columns([2.5, 2, 2, 1.5, 1.5])
    with col1: v_in = st.text_input("Vehículo / Modelo", key=f"v_{st.session_state.count}")
    with col2: r_in = st.text_input("Nombre del Repuesto", key=f"r_{st.session_state.count}")
    with col3: n_in = st.text_input("Número de Parte", key=f"n_{st.session_state.count}")
    with col4: o_in = st.selectbox("Origen", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")
    with col5: t_in = st.selectbox("Tipo de Envío", ["Aéreo", "Marítimo"], key=f"t_{st.session_state.count}")

# 6. LÓGICA DE IA (NIVEL DE PAGO 1 - VERSIÓN V1 ESTABLE)
if st.button("🚀 GENERAR ANÁLISIS Y COTIZACIÓN PROFESIONAL", type="primary"):
    if v_in and r_in and n_in:
        # Uso de la versión v1 estable para evitar el Error 404
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        url_back = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={API_KEY}"
        
        prompt = f"""
        ACTÚA COMO EXPERTO LOGÍSTICO DE LogiPartVE. 
        1. ANÁLISIS TÉCNICO: Referencia {n_in} para {r_in} en vehículo {v_in}. Estima peso/medidas.
        2. COSTOS {o_in.upper()}: MIA Aé ${st.session_state.tarifas['mia_a']}, Mar ${st.session_state.tarifas['mia_m']} | MAD Aé ${st.session_state.tarifas['mad']}.
        3. STATUS RUTA: Alertas aduanas Venezuela Diciembre 2025.
        """

        with st.spinner('Conectando con servidores premium...'):
            try:
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
                if res.status_code ==
