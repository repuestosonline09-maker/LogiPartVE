import streamlit as st
import requests
import json

# 1. Configuración de página
st.set_page_config(page_title="LogiPartVE AI Pro", layout="wide", page_icon="✈️")

# Carga de Secretos Seguros
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASS_ADMIN = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("⚠️ Error: Configure GOOGLE_API_KEY y ADMIN_PASSWORD en los Secrets de Streamlit.")
    st.stop()

# Inicialización de estados
if 'resultado_ia' not in st.session_state:
    st.session_state.resultado_ia = ""
if 'count' not in st.session_state:
    st.session_state.count = 0
if 'tarifas' not in st.session_state:
    st.session_state.tarifas = {"mia_a": 9.0, "mia_m": 40.0, "mad": 20.0}

# 2. Estética Personalizada
st.markdown("""
    <style>
    .report-container { 
        padding: 25px; border-radius: 12px; background-color: #ffffff; 
        border: 2px solid #007bff; color: #1a1a1a; white-space: pre-wrap;
        font-family: Arial, sans-serif;
    }
    .stButton>button { border-radius: 8px; height: 3.5em; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar Administrativo
with st.sidebar:
    st.header("🔐 Panel Master")
    check_pass = st.text_input("Contraseña Admin", type="password")
    if check_pass == PASS_ADMIN:
        st.success("Modo Admin Activo")
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo ($/lb)", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo ($/ft³)", value=st.session_state.tarifas["mia_m"])
        st.session_state.tarifas["mad"] = st.number_input("MAD Aéreo ($/kg)", value=st.session_state.tarifas["mad"])
    else:
        st.info("Panel de Tarifas Bloqueado")

# --- SECCIÓN DEL LOGO Y TÍTULO ---
col_l1, col_l2 = st.columns([1, 4])
with col_l1:
    # PEGA TU ENLACE AQUÍ CUANDO LO TENGAS
    st.image("https://cdn-icons-png.flaticon.com/512/2208/2208233.png", width=120) 
with col_l2:
    st.title("LogiPartVE AI: Cotizador Express")

# 4. Interfaz del Vendedor
with st.container():
    c1, c2 = st.columns(2)
    with c1:
        v_in = st.text_input("🚙 Vehículo (Marca, Modelo, Año, Cilindrada)", key=f"v_{st.session_state.count}")
        r_in = st.text_input("🔧 Repuesto", key=f"r_{st.session_state.count}")
    with c2:
        n_in = st.text_input("🏷️ N° DE PARTE", key=f"n_{st.session_state.count}")
        o_in = st.selectbox("📍 ORIGEN", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")

# 5. Lógica de Petición con CÁLCULOS FORZADOS
if st.button("🚀 GENERAR COTIZACIÓN DE ENVÍO", type="primary"):
    if not v_in or not r_in or not n_in:
        st.warning("⚠️ Datos incompletos.")
    else:
        try:
            url_m = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
            modelos = [m['name'] for m in requests.get(url_m).json().get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
            url = f"https://generativelanguage.googleapis.com/v1beta/{modelos[0]}:generateContent?key={API_KEY}"
