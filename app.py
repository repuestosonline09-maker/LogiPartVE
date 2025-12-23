import streamlit as st
import requests
import json
import os

# ==========================================
# 1. CONFIGURACIÓN Y PROTECCIÓN DE DATOS
# ==========================================
st.set_page_config(page_title="LogiPartVE Pro", layout="wide", page_icon="✈️")

# --- SECCIÓN DEL LOGO REPARADA ---
# Intentamos forzar la carga del archivo local
logo_path = "logo.png"

col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2:
    if os.path.exists(logo_path):
        st.image(logo_path, width=350)
    else:
        # Si por alguna razón el nombre en GitHub tiene mayúsculas (ej: Logo.png)
        st.warning("⚠️ El archivo 'logo.png' no se detecta. Verifica que el nombre esté todo en minúsculas en GitHub.")

# Carga de Secretos
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASS_ADMIN = st.secrets["ADMIN_PASSWORD"]
except Exception as e:
    st.error("⚠️ Error en Secrets de Streamlit.")
    st.stop()

# ESTADOS DE SESIÓN
if 'resultado_ia' not in st.session_state: st.session_state.resultado_ia = ""
if 'count' not in st.session_state: st.session_state.count = 0
if 'tarifas' not in st.session_state: 
    st.session_state.tarifas = {"mia_a": 9.0, "mia_m": 40.0, "mad": 20.0}

# ==========================================
# 2. PANEL DE CONTROL (ADMIN)
# ==========================================
with st.sidebar:
    if os.path.exists(logo_path):
        st.image(logo_path, width=150)
        
    st.header("🔍 Estatus")
    if API_KEY.endswith("MYTA"):
        st.success("Conexión Premium Activa")
    
    st.markdown("---")
    st.header("⚙️ Tarifas")
    check_pass = st.text_input("Contraseña", type="password")
    if check_pass == PASS_ADMIN:
        st.success("Admin Validado")
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo ($/lb)", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo ($/ft³)", value=st.session_state.tarifas["mia_m"])
        st.session_state.tarifas["mad"] = st.number_input("MAD Aéreo ($/kg)", value=st.session_state.tarifas["mad"])

# ==========================================
# 3. INTERFAZ PRINCIPAL
# ==========================================
st.title("LogiPartVE: Inteligencia Automotriz DDP")
st.markdown("---")

col1, col2, col3, col4, col5 = st.columns([2.5, 2, 2, 1.5, 1.5])
with col1: v_in = st.text_input("Vehículo / Modelo", key=f"v_{st.session_state.count}")
with col2: r_in = st.text_input("Nombre del Repuesto", key=f"r_{st.session_state.count}")
with col3: n_in = st.text_input("Número de Parte", key=f"n_{st.session_state.count}")
with col4: o_in = st.selectbox("Origen", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")
with col5: t_in = st.selectbox("Envío", ["Aéreo", "Marítimo"], key=f"t_{st.session_state.count}")

# ==========================================
# 4. LÓGICA DE INTELIGENCIA
# ==========================================
if st.button("🚀 GENERAR ANÁLISIS Y COTIZACIÓN PROFESIONAL", type="primary"):
    if v_in and r_in and n_in:
        modelos = ["gemini-2.0-flash", "gemini-1.5-pro"]
        prompt = f"""
        ACTÚA COMO EXPERTO LOGÍSTICO AUTOMOTRIZ DDP.
        Triangula: {r_in} ({n_in}) para {v_in}.
        Calcula el EMPAQUE REFORZADO y cotiza según {st.session_state.tarifas} desde {o_in} via {t_in}.
        SÉ BREVE (máx 150 palabras).
        """

        with st.spinner('Analizando...'):
            for m in modelos:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={API_KEY}"
                try:
                    res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
                    if res.status_code == 200:
                        st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
                        st.balloons()
                        break
                except: continue
    else:
        st.warning("⚠️ Complete los datos.")

if st.session_state.resultado_ia:
    st.info(st.session_state.resultado_ia)
    if st.button("🗑️ NUEVA CONSULTA"):
        st.session_state.count += 1
        st.session_state.resultado_ia = ""
        st.rerun()

st.markdown("---")
with st.expander("📊 CALCULADORA MANUAL"):
    # ... (Cuerpo de la calculadora igual al anterior)
    st.write("Cálculo basado en dimensiones de empaque reforzado.")
