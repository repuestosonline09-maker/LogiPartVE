import streamlit as st
import requests
import json
import os

# 1. CONFIGURACIÓN PROFESIONAL
st.set_page_config(page_title="LogiPartVE Pro", layout="wide", page_icon="✈️")

# Nombre del archivo en GitHub
logo_filename = "logo.png"

# --- DISEÑO DEL PANEL CENTRAL (LOGOTIPO CENTRADO) ---
col_space1, col_logo_center, col_space2 = st.columns([1, 2, 1])
with col_logo_center:
    if os.path.exists(logo_filename):
        st.image(logo_filename, use_container_width=True)
    else:
        st.info("💡 Cargando logo principal...")

# 2. SEGURIDAD Y ESTADOS DE SESIÓN
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

# --- DISEÑO DE BARRA LATERAL (SIDEBAR CENTRADO) ---
with st.sidebar:
    side_col1, side_col2, side_col3 = st.columns([1, 3, 1])
    with side_col2:
        if os.path.exists(logo_filename):
            st.image(logo_filename, use_container_width=True)
    
    st.markdown("<h2 style='text-align: center;'>Estatus</h2>", unsafe_allow_html=True)
    if API_KEY.endswith("MYTA"):
        st.success("Conexión Premium Activa")
    
    st.markdown("---")
    st.markdown("<h2 style='text-align: center;'>Tarifas Admin</h2>", unsafe_allow_html=True)
    check_pass = st.text_input("Contraseña", type="password")
    if check_pass == PASS_ADMIN:
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo ($/lb)", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo ($/ft³)", value=st.session_state.tarifas["mia_m"])
        st.session_state.tarifas["mad"] = st.number_input("MAD Aéreo ($/kg)", value=st.session_state.tarifas["mad"])

# 3. INTERFAZ DE USUARIO (TÍTULO LIMPIO)
st.markdown("<h1 style='text-align: center;'>Inteligencia Automotriz DDP</h1>", unsafe_allow_html=True)
st.markdown("---")

col1, col2, col3, col4, col5 = st.columns([2.5, 2, 2, 1.5, 1.5])
with col1: v_in = st.text_input("Vehículo / Modelo", key=f"v_{st.session_state.count}")
with col2: r_in = st.text_input("Nombre del Repuesto", key=f"r_{st.session_state.count}")
with col3: n_in = st.text_input("Número de Parte", key=f"n_{st.session_state.count}")
with col4: o_in = st.selectbox("Origen", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")
with col5: t_in = st.selectbox("Envío", ["Aéreo", "Marítimo"], key=f"t_{st.session_state.count}")

# 4. MOTOR DE INTELIGENCIA
if st.button("🚀 GENERAR ANÁLISIS Y COTIZACIÓN PROFESIONAL", type="primary", use_container_width=True):
    if v_in and r_in and n_in:
        prompt = f"""
        ACTÚA COMO EXPERTO LOGÍSTICO AUTOMOTRIZ DDP PARA LogiPartVE.
        1. Triangula: {r_in} ({n_in}) para {v_in}. Valida compatibilidad técnica.
        2. Empaque: Estima medidas reales y calcula dimensiones de EMPAQUE REFORZADO para envío internacional.
        3. Costos: Cotiza DDP basado en el volumen del EMPAQUE REFORZADO usando {st.session_state.tarifas} (Origen: {o_in}, Tipo: {t_in}).
        SÉ BREVE (máx 150 palabras). No saludes.
        """
        
        with st.spinner('Procesando análisis técnico...'):
            modelos = ["gemini-2.0-flash", "gemini-1.5-pro"]
            exito = False
            for m in modelos:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={API_KEY}"
                try:
                    res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
                    if res.status_code == 200:
                        st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
                        st.balloons()
                        exito = True
                        break
                except: continue
            if not exito: st.error("Error de conexión con la IA.")
    else:
        st.warning("⚠️ Complete todos los campos para triangular la información.")

# 5. RESULTADOS
if st.session_state.resultado_ia:
    st.markdown("### 📝 Análisis y Cotización Final")
    st.info(st.session_state.resultado_ia)
    if st.button("🗑️ NUEVA CONSULTA", use_container_width=True):
        st.session_state.count += 1
        st.session_state.resultado_ia = ""
        st.rerun()

st.markdown("---")
# 6. CALCULADORA MANUAL (CORREGIDA)
with st.expander("📊 CALCULADORA MANUAL"):
    st.write("Cálculos matemáticos directos basados en empaque reforzado.")
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1: l_cm = st.number_input("Largo (cm)", min_value=0.0)
    with mc2: an_cm = st.number_input("Ancho (cm)", min_value=0.0)
    with mc3: al_cm = st.number_input("Alto (cm)", min_value=0.0)
    with mc4: p_kg = st.number_input("Peso (kg)", min_value=0.0)
    
    if st.button("🧮 CALCULAR MANUAL"):
        p_v = (l_cm * an_cm * al_cm) / 5000
        p_f = max(p_kg, p_v)
        st.success(f"Peso facturable: {p_f:.2f} kg/lb | Estimado: ${p_f * st.session_state.tarifas['mia_a']:.2f}")
