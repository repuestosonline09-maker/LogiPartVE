import streamlit as st
import requests
import json

# 1. CONFIGURACIÓN E IDENTIDAD
st.set_page_config(page_title="LogiPartVE Pro", layout="wide", page_icon="✈️")

# Carga de Secretos
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASS_ADMIN = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("⚠️ Error: Configure 'Secrets' en Streamlit.")
    st.stop()

# ESTADOS DE SESIÓN (MEMORIA)
if 'resultado_ia' not in st.session_state: st.session_state.resultado_ia = ""
if 'count' not in st.session_state: st.session_state.count = 0
if 'tarifas' not in st.session_state: st.session_state.tarifas = {"mia_a": 9.0, "mia_m": 40.0, "mad": 20.0}

# 2. CSS PARA DISEÑO PROFESIONAL
st.markdown("""
    <style>
    .block-container {padding-top: 1rem;}
    .report-container { 
        padding: 20px; border-radius: 10px; background-color: #ffffff; 
        border: 2px solid #007bff; color: #1e1e1e;
    }
    .manual-table { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #dee2e6; }
    </style>
""", unsafe_allow_html=True)

# 3. PANEL DE ADMINISTRACIÓN (TARIFAS)
with st.sidebar:
    st.header("⚙️ Admin")
    check_pass = st.text_input("Contraseña", type="password")
    if check_pass == PASS_ADMIN:
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo ($/lb)", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo ($/ft³)", value=st.session_state.tarifas["mia_m"])
        st.session_state.tarifas["mad"] = st.number_input("MAD Aéreo ($/kg)", value=st.session_state.tarifas["mad"])

# 4. ENCABEZADO Y FORMULARIO
st.title("LogiPartVE: Gestión Experta DDP")
with st.container():
    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
    with col1: v_in = st.text_input("Vehículo", key=f"v_{st.session_state.count}")
    with col2: r_in = st.text_input("Repuesto", key=f"r_{st.session_state.count}")
    with col3: n_in = st.text_input("N° Parte", key=f"n_{st.session_state.count}")
    with col4: o_in = st.selectbox("Origen", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")
    with col5: t_in = st.selectbox("Envío", ["Aéreo", "Marítimo"], key=f"t_{st.session_state.count}")

# 5. LÓGICA DE IA (Sincronización de Saldo)
if st.button("🚀 GENERAR ANÁLISIS Y COTIZACIÓN", type="primary"):
    if v_in and r_in and n_in:
        # Usamos la versión de la API que fuerza la lectura de la cuenta de facturación LogiPartVE3
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        
        prompt = f"""
        EXPERTO LOGÍSTICO LogiPartVE. 
        1. ANALIZA: {r_in} ({n_in}) para {v_in}. Estima peso/medidas.
        2. COTIZA DDP {o_in.upper()} {t_in.upper()}: Tarifas MIA Aé ${st.session_state.tarifas['mia_a']}, Mar ${st.session_state.tarifas['mia_m']} | MAD Aé ${st.session_state.tarifas['mad']}.
        3. ADUANA: Alertas Venezuela Diciembre 2025.
        """

        with st.spinner('Sincronizando créditos y generando...'):
            try:
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                if res.status_code == 200:
                    st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
                elif res.status_code == 404:
                    st.error("⚠️ Error 404: Google aún no propaga tu saldo comercial a este proyecto. Por favor, ve a Google AI Studio, crea una NUEVA API KEY y pégala en tus Secrets. La llave vieja puede estar bloqueada.")
                else:
                    st.error(f"Error {res.status_code}: {res.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Faltan datos.")

# 6. RESULTADOS Y CALCULADORA MANUAL COMPLETA
if st.session_state.resultado_ia:
    st.markdown(f'<div class="report-container">{st.session_state.resultado_ia}</div>', unsafe_allow_html=True)
    if st.button("🗑️ LIMPIAR"):
        st.session_state.count += 1
        st.session_state.resultado_ia = ""
        st.rerun()

st.markdown("---")
st.markdown('<div class="manual-table">', unsafe_allow_html=True)
st.subheader("📊 Calculadora Manual LogiPartVE")
mc1, mc2, mc3, mc4 = st.columns(4)
with mc1: l = st.number_input("Largo (cm)", min_value=0.0)
with mc2: an = st.number_input("Ancho (cm)", min_value=0.0)
with mc3: al = st.number_input("Alto (cm)", min_value=0.0)
with mc4: p = st.number_input("Peso (kg)", min_value=0.0)

if st.button("🧮 CALCULAR COSTO"):
    p_vol = (l * an * al) / 5000
    p_final = max(p, p_vol)
    if o_in == "Miami":
        t = st.session_state.tarifas["mia_a"] if t_in == "Aéreo" else st.session_state.tarifas["mia_m"]
        final = max(p_final * 2.20462 * t, 25.0) if t_in == "Aéreo" else (l*an*al/28316.8) * t
    else:
        final = max(p_final * st.session_state.tarifas["mad"], 25.0)
    st.success(f"**Costo Estimado: ${final:.2f} USD**")
st.markdown('</div>', unsafe_allow_html=True)
