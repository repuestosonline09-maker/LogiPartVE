import streamlit as st
import google.generativeai as genai
import time

# 1. Configuración de página
st.set_page_config(page_title="LogiPartVE Pro", layout="wide", page_icon="✈️")

# Carga de Secretos y Configuración de IA
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASS_ADMIN = st.secrets["ADMIN_PASSWORD"]
    # Configuramos la librería oficial
    genai.configure(api_key=API_KEY)
except:
    st.error("⚠️ Error: Configure 'Secrets' en Streamlit.")
    st.stop()

# Estados de sesión
if 'resultado_ia' not in st.session_state: st.session_state.resultado_ia = ""
if 'count' not in st.session_state: st.session_state.count = 0
if 'tarifas' not in st.session_state: st.session_state.tarifas = {"mia_a": 9.0, "mia_m": 40.0, "mad": 20.0}

# 2. CSS Ultra-Compacto
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    .report-container { 
        padding: 15px; border-radius: 10px; background-color: #ffffff; 
        border: 2px solid #007bff; font-size: 14px; line-height: 1.3;
    }
    .manual-table { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-top: 10px; border: 1px solid #d1d5db; }
    .stButton>button {height: 2.8em;}
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar (Admin)
with st.sidebar:
    check_pass = st.text_input("Admin", type="password")
    if check_pass == PASS_ADMIN:
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo ($/lb)", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo ($/ft³)", value=st.session_state.tarifas["mia_m"])
        st.session_state.tarifas["mad"] = st.number_input("MAD Aéreo ($/kg)", value=st.session_state.tarifas["mad"])

# 4. Encabezado
c1, c2 = st.columns([1, 5])
with c1: st.image("https://cdn-icons-png.flaticon.com/512/2208/2208233.png", width=60) 
with c2: st.title("LogiPartVE: Gestión Experta DDP")

# 5. Formulario Principal
with st.container():
    col1, col2, col3, col4, col5 = st.columns([2.5, 2, 2, 1.2, 1.2])
    with col1: v_in = st.text_input("Vehículo", key=f"v_{st.session_state.count}")
    with col2: r_in = st.text_input("Repuesto", key=f"r_{st.session_state.count}")
    with col3: n_in = st.text_input("N° Parte", key=f"n_{st.session_state.count}")
    with col4: o_in = st.selectbox("Origen", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")
    with col5: t_in = st.selectbox("Envío", ["Aéreo", "Marítimo"], key=f"t_{st.session_state.count}")

# 6. Lógica de IA Profesional
if st.button("🚀 GENERAR ANÁLISIS Y COTIZACIÓN", type="primary"):
    if v_in and r_in and n_in:
        try:
            with st.spinner('Analizando con prioridad de pago...'):
                # Usamos la librería oficial que autogestiona el Nivel de Pago
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                EXPERTO LOGÍSTICO LogiPartVE. 
                1. TÉCNICO: Referencia {n_in} para {r_in} ({v_in}).
                2. COSTOS {o_in.upper()}: Tarifas MIA Aé ${st.session_state.tarifas['mia_a']}, Mar ${st.session_state.tarifas['mia_m']} | MAD Aé ${st.session_state.tarifas['mad']}.
                3. ALERTAS: Diciembre 2025 ruta {o_in} a Venezuela.
                """
                
                response = model.generate_content(prompt)
                st.session_state.resultado_ia = response.text
                
        except Exception as e:
            # Si el modelo flash falla por activación, intentamos con Pro
            try:
                model_pro = genai.GenerativeModel('gemini-1.5-pro')
                response = model_pro.generate_content(prompt)
                st.session_state.resultado_ia = response.text
            except Exception as e2:
                st.error(f"Google está terminando de activar tu cuenta. Espera 2 minutos. Error: {str(e2)}")
    else:
        st.warning("Faltan datos.")

# 7. Resultados
if st.session_state.resultado_ia:
    st.markdown(f'<div class="report-container">{st.session_state.resultado_ia}</div>', unsafe_allow_html=True)
    c_dw, c_cl = st.columns([5, 1])
    with c_dw: st.download_button("📥 Descargar", st.session_state.resultado_ia, file_name="cotizacion.txt")
    with c_cl: 
        if st.button("🗑️ LIMPIAR"):
            st.session_state.count += 1
            st.session_state.resultado_ia = ""
            st.rerun()

# 8. TABLA MANUAL (Seguridad)
st.markdown('<div class="manual-table">', unsafe_allow_html=True)
st.markdown("### 📊 Validación Manual")
mc1, mc2, mc3, mc4 = st.columns(4)
with mc1: l_cm = st.number_input("Largo (cm)", min_value=0.0, key="ml_fin")
with mc2: an_cm = st.number_input("Ancho (cm)", min_value=0.0, key="man_fin")
with mc3: al_cm = st.number_input("Alto (cm)", min_value=0.0, key="mal_fin")
with mc4: p_kg = st.number_input("Peso (kg)", min_value=0.0, key="mp_fin")

if st.button("🧮 CALCULAR MANUAL"):
    p_vol_kg = (l_cm * an_cm * al_cm) / 5000
    p_final_kg = max(p_kg, p_vol_kg)
    costo = p_final_kg * st.session_state.tarifas["mia_a"]
    st.success(f"**Costo: ${costo:.2f} USD**")
st.markdown('</div>', unsafe_allow_html=True)
