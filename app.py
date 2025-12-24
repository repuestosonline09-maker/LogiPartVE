import streamlit as st
import requests
import json
import os
import base64

# 1. CONFIGURACIÓN DE PÁGINA PROFESIONAL
st.set_page_config(page_title="LogiPartVE Pro", layout="wide", page_icon="✈️")

# Nombre del archivo de imagen
logo_filename = "logo.png"

# --- LÓGICA DE DISEÑO ADAPTABLE (CSS) ---
st.markdown(
    """
    <style>
    @media (max-width: 640px) {
        .main-logo-container { width: 120px !important; margin: 0 auto; }
    }
    @media (min-width: 641px) {
        .main-logo-container { width: 180px !important; margin: 0 auto; }
    }
    .stImage > img {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 2. CARGA DE SECRETOS Y SEGURIDAD
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASS_ADMIN = st.secrets["ADMIN_PASSWORD"]
except Exception:
    st.error("⚠️ Error crítico: Configure 'Secrets' en Streamlit Cloud.")
    st.stop()

# ESTADOS DE SESIÓN
if 'resultado_ia' not in st.session_state: st.session_state.resultado_ia = ""
if 'count' not in st.session_state: st.session_state.count = 0
if 'tarifas' not in st.session_state: 
    st.session_state.tarifas = {"mia_a": 9.0, "mia_m": 40.0, "mad": 20.0}

# --- PANEL CENTRAL: LOGOTIPO INTELIGENTE ---
c_left, c_logo, c_right = st.columns([1.5, 1, 1.5])
with c_logo:
    if os.path.exists(logo_filename):
        with open(logo_filename, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        st.markdown(f'<div class="main-logo-container"><img src="data:image/png;base64,{data}" style="width:100%"></div>', unsafe_allow_html=True)
    else:
        st.info("💡 Cargando logo...")

# --- BARRA LATERAL (ADMIN) ---
with st.sidebar:
    sc1, sc2, sc3 = st.columns([1, 2, 1])
    with sc2:
        if os.path.exists(logo_filename):
            st.image(logo_filename, use_container_width=True)
    
    st.markdown("<h2 style='text-align: center; font-size: 18px;'>Estatus</h2>", unsafe_allow_html=True)
    if API_KEY:
        st.success("Conexión Premium Activa")
    
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; font-size: 18px;'>Tarifas Admin</h2>", unsafe_allow_html=True)
    check_pass = st.text_input("Contraseña", type="password")
    
    if check_pass == PASS_ADMIN:
        st.success("Acceso Autorizado")
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo ($/lb)", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo ($/ft³)", value=st.session_state.tarifas["mia_m"])
        st.session_state.tarifas["mad"] = st.number_input("MAD Aéreo ($/kg)", value=st.session_state.tarifas["mad"])

# 3. TÍTULO PRINCIPAL
st.markdown("<h1 style='text-align: center; color: #1E3A8A; font-size: 32px; margin-top: -10px;'>Inteligencia Automotriz DDP</h1>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# 4. FORMULARIO DE CONSULTA
col1, col2, col3, col4, col5 = st.columns([2.5, 2, 2, 1.5, 1.5])
with col1: v_in = st.text_input("Vehículo / Modelo", key=f"v_{st.session_state.count}")
with col2: r_in = st.text_input("Nombre del Repuesto", key=f"r_{st.session_state.count}")
with col3: n_in = st.text_input("Número de Parte", key=f"n_{st.session_state.count}")
with col4: o_in = st.selectbox("Origen", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")
with col5: t_in = st.selectbox("Envío", ["Aéreo", "Marítimo"], key=f"t_{st.session_state.count}")

# 5. MOTOR DE INTELIGENCIA (DDP PUERTA A PUERTA CON CONVERSIÓN)
if st.button("🚀 GENERAR ANÁLISIS Y COTIZACIÓN PROFESIONAL", type="primary", use_container_width=True):
    if v_in and r_in and n_in:
        # VALIDACIÓN LOGÍSTICA
        if o_in == "Madrid" and t_in == "Marítimo":
            st.error("⚠️ Error de Ruta: Desde Madrid solo operamos envíos AÉREOS.")
            st.stop()

        # PROMPT CON LÓGICA DE UNIDADES
        prompt = f"""
        ACTÚA COMO EXPERTO LOGÍSTICO AUTOMOTRIZ DDP PARA LogiPartVE.
        
        DATOS:
        - Repuesto: {r_in} ({n_in}) para {v_in}
        - Ruta: {o_in} -> Venezuela vía {t_in}
        - Tarifas: {st.session_state.tarifas}

        REGLAS DE CÁLCULO ESTRICTAS (PUERTA A PUERTA):
        1. Si es MIAMI AÉREO: Estima peso en Kilos, pero CONVIÉRTELO a Libras (1 kg = 2.20462 lb) y multiplica por {st.session_state.tarifas['mia_a']} $/lb.
        2. Si es MADRID AÉREO: Calcula directamente en KILOS por la tarifa {st.session_state.tarifas['mad']} $/kg.
        3. Si es MIAMI MARÍTIMO: Calcula el volumen en Pies Cúbicos (ft³) por la tarifa {st.session_state.tarifas['mia_m']} $/ft³.
        
        INSTRUCCIONES:
        - Valida compatibilidad técnica.
        - Estima dimensiones y peso del EMPAQUE REFORZADO.
        - Muestra el cálculo: "Peso/Volumen estimado -> Tarifa aplicada".
        - NO sumes gastos extras (Aduana/Arancel ya incluidos).
        
        SÉ BREVE (Máx 150 palabras).
        """
        
        with st.spinner('Triangulando información y calculando unidades...'):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
                if res.status_code == 200:
                    st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
                    st.balloons()
                else:
                    st.error(f"Error en IA: {res.status_code}")
            except Exception as e:
                st.error(f"Error de red: {str(e)}")
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

# 7. CALCULADORA MANUAL (AÉREO VS MARÍTIMO + MÍNIMO $25)
with st.expander("📊 CALCULADORA MANUAL"):
    st.write("Cálculo automático de Peso Volumétrico / Pies Cúbicos y Tarifa Mínima.")
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1: l_cm = st.number_input("Largo (cm)", min_value=0.0, format="%.1f")
    with mc2: an_cm = st.number_input("Ancho (cm)", min_value=0.0, format="%.1f")
    with mc3: al_cm = st.number_input("Alto (cm)", min_value=0.0, format="%.1f")
    with mc4: p_kg = st.number_input("Peso Real (kg)", min_value=0.0, format="%.1f")
    
    if st.button("🧮 CALCULAR MANUALMENTE"):
        # Cálculos Base
        vol_cm3 = l_cm * an_cm * al_cm
        p_vol = vol_cm3 / 5000
        p_mayor_kg = max(p_kg, p_vol)
        
        if o_in == "Miami" and t_in == "Marítimo":
            # REGLA MARÍTIMA: Pies Cúbicos (1 ft3 = 28316.8 cm3)
            ft3 = vol_cm3 / 28316.8
            total_previo = ft3 * st.session_state.tarifas['mia_m']
            p_display, unit = ft3, "ft³"
            tarifa_val = st.session_state.tarifas['mia_m']
        
        elif o_in == "Madrid":
            # REGLA MADRID: Kilos
            total_previo = p_mayor_kg * st.session_state.tarifas['mad']
            p_display, unit = p_mayor_kg, "kg"
            tarifa_val = st.session_state.tarifas['mad']
            
        else: # Miami Aéreo
            # REGLA MIAMI AÉREO: Libras
            p_lb = p_mayor_kg * 2.20462
            total_previo = p_lb * st.session_state.tarifas['mia_a']
            p_display, unit = p_lb, "lb"
            tarifa_val = st.session_state.tarifas['mia_a']

        # Aplicación del Mínimo de $25 (Aplica a todas las rutas)
        if total_previo < 25:
            st.warning(f"El cálculo arroja ${total_previo:.2f}, pero se aplica la Tarifa Mínima de $25.00.")
            total_final = 25.0
        else:
            total_final = total_previo
            
        st.success(f"Dato Facturable: {p_display:.2f} {unit} | Tarifa: ${tarifa_val} | TOTAL DDP: ${total_final:.2f}")
