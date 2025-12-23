import streamlit as st
import requests
import json

# ==========================================
# 1. CONFIGURACIÓN Y PROTECCIÓN DE DATOS
# ==========================================
st.set_page_config(page_title="LogiPartVE Pro", layout="wide", page_icon="✈️")

# --- SECCIÓN DEL LOGO (Cargando desde GitHub) ---
col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2:
    try:
        # Intentamos cargar el logo que subiste
        st.image("logo.png", width=350)
    except:
        st.info("💡 Logo en proceso de carga...")
# -----------------------------------------------

# Carga de Secretos (Validada para llave MYTA)
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASS_ADMIN = st.secrets["ADMIN_PASSWORD"]
except Exception as e:
    st.error("⚠️ ERROR CRÍTICO EN SECRETS: Verifique la configuración en Streamlit Cloud.")
    st.stop()

# ESTADOS DE SESIÓN
if 'resultado_ia' not in st.session_state: st.session_state.resultado_ia = ""
if 'count' not in st.session_state: st.session_state.count = 0
if 'tarifas' not in st.session_state: 
    st.session_state.tarifas = {"mia_a": 9.0, "mia_m": 40.0, "mad": 20.0}

# ==========================================
# 2. PANEL DE CONTROL (ADMIN & ESTATUS)
# ==========================================
with st.sidebar:
    try:
        st.image("logo.png", width=150)
    except:
        pass
        
    st.header("🔍 Estatus de Sistema")
    if API_KEY.endswith("MYTA"):
        st.success("Conexión Premium: ACTIVA")
    
    st.markdown("---")
    st.header("⚙️ Gestión de Tarifas")
    check_pass = st.text_input("Contraseña de Acceso", type="password")
    if check_pass == PASS_ADMIN:
        st.success("Perfil Administrador: Validado")
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo ($/lb)", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo ($/ft³)", value=st.session_state.tarifas["mia_m"])
        st.session_state.tarifas["mad"] = st.number_input("MAD Aéreo ($/kg)", value=st.session_state.tarifas["mad"])

# ==========================================
# 3. INTERFAZ LOGÍSTICA
# ==========================================
st.title("LogiPartVE: Inteligencia Automotriz DDP")
st.markdown("---")

# Formulario de entrada
col1, col2, col3, col4, col5 = st.columns([2.5, 2, 2, 1.5, 1.5])
with col1: v_in = st.text_input("Vehículo / Modelo", key=f"v_{st.session_state.count}")
with col2: r_in = st.text_input("Nombre del Repuesto", key=f"r_{st.session_state.count}")
with col3: n_in = st.text_input("Número de Parte", key=f"n_{st.session_state.count}")
with col4: o_in = st.selectbox("Origen", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")
with col5: t_in = st.selectbox("Envío", ["Aéreo", "Marítimo"], key=f"t_{st.session_state.count}")

# ==========================================
# 4. CÓDIGO DE COMUNICACIÓN PROTEGIDO
# ==========================================
if st.button("🚀 GENERAR ANÁLISIS Y COTIZACIÓN PROFESIONAL", type="primary"):
    if v_in and r_in and n_in:
        modelos_a_probar = ["gemini-2.0-flash", "gemini-1.5-pro"]
        
        prompt = f"""
        ACTÚA COMO UN EXPERTO EN REPUESTOS AUTOMOTRICES Y LOGÍSTICA DDP.
        
        DATOS: Vehículo: {v_in} | Repuesto: {r_in} | N° Parte: {n_in}.
        RUTA: {o_in} -> Venezuela ({t_in}).
        TARIFAS: {st.session_state.tarifas}.

        TAREAS CRÍTICAS:
        1. TRIANGULACIÓN: Valida si {n_in} es para {r_in} en {v_in}. Indica sustitutos/actualizaciones.
        2. EMPAQUE REFORZADO: Estima medidas y peso real de la pieza. Calcula las dimensiones del EMPAQUE REFORZADO necesario para protección internacional.
        3. COTIZACIÓN DDP: Calcula costo final basado en el volumen/peso del EMPAQUE REFORZADO y las tarifas dadas.
        4. ADUANA: Alertas Venezuela DDP para este repuesto.
        
        FORMATO: Máximo 150 palabras. Directo al grano.
        """

        with st.spinner('Triangulando información y calculando empaques...'):
            exito = False
            for m_name in modelos_a_probar:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m_name}:generateContent?key={API_KEY}"
                try:
                    res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
                    if res.status_code == 200:
                        st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
                        st.balloons()
                        exito = True
                        break
                except:
                    continue
            
            if not exito:
                st.error("⚠️ Error de Redundancia: Google no respondió.")
    else:
        st.warning("⚠️ Por favor, complete la información para triangular.")

# ==========================================
# 5. RESULTADOS Y CALCULADORA
# ==========================================
if st.session_state.resultado_ia:
    st.markdown("### 📝 Análisis Técnico y Cotización")
    st.info(st.session_state.resultado_ia)
    
    if st.button("🗑️ NUEVA CONSULTA"):
        st.session_state.count += 1
        st.session_state.resultado_ia = ""
        st.rerun()

st.markdown("---")
with st.expander("📊 CALCULADORA MANUAL DE RESPALDO"):
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1: l_cm = st.number_input("Largo (cm)", min_value=0.0)
    with mc2: an_cm = st.number_input("Ancho (cm)", min_value=0.0)
    with mc3: al_cm = st.number_input("Alto (cm)", min_value=0.0)
    with mc4: p_kg = st.number_input("Peso (kg)", min_value=0.0)
    if st.button("🧮 CALCULAR"):
        p_v = (l_cm * an_cm * al_cm) / 5000
        p_f = max(p_kg, p_v)
        st.success(f"Peso facturable: {p_f:.2f} kg/lb | Estimado: ${p_f * st.session_state.tarifas['mia_a']:.2f}")
