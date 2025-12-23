import streamlit as st
import requests
import json
import os

# 1. CONFIGURACIÓN DE PÁGINA (UI/UX PREMIUM)
st.set_page_config(page_title="LogiPartVE Pro", layout="wide", page_icon="✈️")

# Nombre del archivo en GitHub
logo_filename = "logo.png"

# --- DISEÑO DEL PANEL CENTRAL (EL BALANCE DEL DISEÑADOR) ---
# Usamos una proporción [1.5, 1, 1.5] para que el logo tenga presencia pero no invada
c_left, c_logo, c_right = st.columns([1.5, 1, 1.5])
with c_logo:
    if os.path.exists(logo_filename):
        # 180px es el tamaño ideal para que el detalle del logo sea legible y estético
        st.image(logo_filename, use_container_width=True)
    else:
        st.info("💡 Cargando Identidad...")

# 2. SEGURIDAD Y LOGICA DE NEGOCIO
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASS_ADMIN = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("⚠️ Error: Configure 'Secrets' en Streamlit Cloud.")
    st.stop()

if 'resultado_ia' not in st.session_state: st.session_state.resultado_ia = ""
if 'count' not in st.session_state: st.session_state.count = 0
if 'tarifas' not in st.session_state: 
    st.session_state.tarifas = {"mia_a": 9.0, "mia_m": 40.0, "mad": 20.0}

# --- BARRA LATERAL (CONSERVA TU DISEÑO FAVORITO) ---
with st.sidebar:
    side_c1, side_c2, side_c3 = st.columns([1, 2, 1])
    with side_c2:
        if os.path.exists(logo_filename):
            st.image(logo_filename, use_container_width=True)
    
    st.markdown("<h2 style='text-align: center; font-size: 18px;'>Estatus</h2>", unsafe_allow_html=True)
    if API_KEY.endswith("MYTA"):
        st.success("Conexión Premium Activa")
    
    st.markdown("---")
    check_pass = st.text_input("Contraseña Admin", type="password")
    if check_pass == PASS_ADMIN:
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo ($/lb)", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo ($/ft³)", value=st.session_state.tarifas["mia_m"])

# 3. TITULAR PROFESIONAL
st.markdown("<h1 style='text-align: center; color: #1E3A8A; font-size: 32px; margin-top: -20px;'>Inteligencia Automotriz DDP</h1>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# 4. FORMULARIO OPERATIVO
col1, col2, col3, col4, col5 = st.columns([2.5, 2, 2, 1.5, 1.5])
with col1: v_in = st.text_input("Vehículo / Modelo", key=f"v_{st.session_state.count}")
with col2: r_in = st.text_input("Nombre del Repuesto", key=f"r_{st.session_state.count}")
with col3: n_in = st.text_input("Número de Parte", key=f"n_{st.session_state.count}")
with col4: o_in = st.selectbox("Origen", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")
with col5: t_in = st.selectbox("Envío", ["Aéreo", "Marítimo"], key=f"t_{st.session_state.count}")

# 5. MOTOR DE INTELIGENCIA
if st.button("🚀 GENERAR ANÁLISIS Y COTIZACIÓN PROFESIONAL", type="primary", use_container_width=True):
    if v_in and r_in and n_in:
        prompt = f"""
        ACTÚA COMO EXPERTO LOGÍSTICO AUTOMOTRIZ DDP.
        1. Triangula: {r_in} ({n_in}) para {v_in}. Valida compatibilidad técnica.
        2. Empaque: Estima medidas y peso. Calcula medidas de EMPAQUE REFORZADO.
        3. Costos: Cotiza DDP con {st.session_state.tarifas} ({o_in}, {t_in}).
        SÉ BREVE (máx 150 palabras).
        """
        with st.spinner('Procesando análisis técnico...'):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
                if res.status_code == 200:
                    st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
                    st.balloons()
                else: st.error("Error en respuesta de IA.")
            except: st.error("Error de conexión.")
    else:
        st.warning("⚠️ Complete todos los campos.")

# 6. RESULTADOS
if st.session_state.resultado_ia:
    st.markdown("### 📝 Análisis y Cotización Final")
    st.info(st.session_state.resultado_ia)
    if st.button("🗑️ NUEVA CONSULTA", use_container_width=True):
        st.session_state.count += 1
        st.session_state.resultado_ia = ""
        st.rerun()

st.markdown("---")
# 7. CALCULADORA MANUAL
with st.expander("📊 CALCULADORA MANUAL"):
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1: l_cm = st.number_input("Largo (cm)", min_value=0.0, format="%.1f")
    with mc2: an_cm = st.number_input("Ancho (cm)", min_value=0.0, format="%.1f")
    with mc3: al_cm = st.number_input("Alto (cm)", min_value=0.0, format="%.1f")
    with mc4: p_kg = st.number_input("Peso (kg)", min_value=0.0, format="%.1f")
    if st.button("🧮 CALCULAR MANUAL"):
        p_v = (l_cm * an_cm * al_cm) / 5000
        p_f = max(p_kg, p_v)
        st.success(f"Peso facturable: {p_f:.2f} | Estimado: ${p_f * st.session_state.tarifas['mia_a']:.2f}")
