import streamlit as st
import requests
import json
import os
import base64

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="LogiPartVE Pro", layout="wide", page_icon="✈️")

logo_filename = "logo.png"

# --- DISEÑO RESPONSIVE ---
st.markdown("""
    <style>
    @media (max-width: 640px) { .main-logo-container { width: 120px !important; margin: 0 auto; } }
    @media (min-width: 641px) { .main-logo-container { width: 180px !important; margin: 0 auto; } }
    .stImage > img { display: block; margin-left: auto; margin-right: auto; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE SECRETOS
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASS_ADMIN = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("⚠️ Error: Configure 'Secrets' en Streamlit.")
    st.stop()

if 'resultado_ia' not in st.session_state: st.session_state.resultado_ia = ""
if 'count' not in st.session_state: st.session_state.count = 0
if 'tarifas' not in st.session_state: 
    st.session_state.tarifas = {"mia_a": 9.0, "mia_m": 40.0, "mad": 20.0}

# --- PANEL CENTRAL: LOGOTIPO ---
c_left, c_logo, c_right = st.columns([1.5, 1, 1.5])
with c_logo:
    if os.path.exists(logo_filename):
        with open(logo_filename, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        st.markdown(f'<div class="main-logo-container"><img src="data:image/png;base64,{data}" style="width:100%"></div>', unsafe_allow_html=True)

# --- BARRA LATERAL (ADMIN) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>Configuración</h2>", unsafe_allow_html=True)
    check_pass = st.text_input("Contraseña Admin", type="password")
    if check_pass == PASS_ADMIN:
        st.success("Acceso Autorizado")
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo ($/lb)", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo ($/ft³)", value=st.session_state.tarifas["mia_m"])
        st.session_state.tarifas["mad"] = st.number_input("MAD Aéreo ($/kg)", value=st.session_state.tarifas["mad"])

# 3. INTERFAZ PRINCIPAL
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>Inteligencia Automotriz DDP</h1>", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns([2.5, 2, 2, 1.5, 1.5])
with col1: v_in = st.text_input("Vehículo", key=f"v_{st.session_state.count}")
with col2: r_in = st.text_input("Repuesto", key=f"r_{st.session_state.count}")
with col3: n_in = st.text_input("N° Parte", key=f"n_{st.session_state.count}")
with col4: o_in = st.selectbox("Origen", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")
with col5: t_in = st.selectbox("Envío", ["Aéreo", "Marítimo"], key=f"t_{st.session_state.count}")

# 5. MOTOR DE INTELIGENCIA (ELIMINANDO ERRORES DE CÁLCULO)
if st.button("🚀 GENERAR ANÁLISIS Y COTIZACIÓN", type="primary", use_container_width=True):
    if v_in and r_in and n_in:
        if o_in == "Madrid" and t_in == "Marítimo":
            st.error("⚠️ Madrid solo permite envíos Aéreos.")
            st.stop()

        prompt = f"""
        ERES EL EXPERTO SENIOR EN LOGÍSTICA AUTOMOTRIZ DE LogiPartVE. 
        Tu misión es COTIZAR DE FORMA AUTÓNOMA. No pidas datos al usuario.

        PRODUCTO: {r_in} ({n_in}) para {v_in}.
        RUTA: {o_in} -> Venezuela vía {t_in}.
        TARIFAS DISPONIBLES (Monto por unidad): {st.session_state.tarifas}

        INSTRUCCIONES OBLIGATORIAS:
        1. DETERMINA LAS MEDIDAS: Basado en tu base de datos de autopartes, establece las dimensiones (cm) y peso (kg) que tendrá este repuesto ya protegido con un EMPAQUE REFORZADO. No preguntes, ¡TÚ ERES EL EXPERTO!
        
        2. CÁLCULO LOGÍSTICO:
           - Calcula Peso Volumétrico (LxAnxAl/5000).
           - Determina el PESO FACTURABLE (El mayor entre Real y Volumétrico).
           - Si la ruta es MIAMI AÉREO: Convierte a Libras (x 2.20462) y multiplica ÚNICAMENTE por {st.session_state.tarifas['mia_a']}.
           - Si la ruta es MADRID AÉREO: Usa Kilos y multiplica ÚNICAMENTE por {st.session_state.tarifas['mad']}.
           - Si es MIAMI MARÍTIMO: Calcula Pies Cúbicos (cm3/28316.8) y multiplica por {st.session_state.tarifas['mia_m']}.

        3. REGLA DEL MÍNIMO: Si el resultado es menor a $25.00, establece el COSTO TOTAL en $25.00 e indica: "⚠️ Se aplica tarifa mínima de envío ($25.00)".

        4. PROHIBICIÓN: No menciones aranceles extra, no sumes las tarifas de otras rutas. El resultado es TODO INCLUIDO PUERTA A PUERTA.

        FORMATO DE RESPUESTA:
        - Análisis técnico breve de la pieza.
        - Especificaciones del empaque reforzado que TÚ definiste.
        - COSTO TOTAL DDP: $XX.XX USD.
        """
        
        with st.spinner('Procesando...'):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
                if res.status_code == 200:
                    st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
                    st.balloons()
            except: st.error("Error de conexión.")
    else: st.warning("⚠️ Complete los campos.")

if st.session_state.resultado_ia:
    st.info(st.session_state.resultado_ia)
    if st.button("🗑️ NUEVA CONSULTA"):
        st.session_state.count += 1
        st.session_state.resultado_ia = ""
        st.rerun()

st.markdown("---")

# 7. CALCULADORA MANUAL (REESTRUCTURADA)
with st.expander("📊 CALCULADORA MANUAL"):
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1: l_cm = st.number_input("Largo (cm)", min_value=0.0)
    with mc2: an_cm = st.number_input("Ancho (cm)", min_value=0.0)
    with mc3: al_cm = st.number_input("Alto (cm)", min_value=0.0)
    with mc4: p_kg_in = st.number_input("Peso Real (kg)", min_value=0.0)
    
    if st.button("🧮 CALCULAR"):
        vol_cm3 = l_cm * an_cm * al_cm
        p_vol = vol_cm3 / 5000
        p_mayor_kg = max(p_kg_in, p_vol)
        
        # Iniciar cálculo de costo base
        costo_calculado = 0.0
        detalle_u = ""

        if o_in == "Miami" and t_in == "Marítimo":
            pies_c = vol_cm3 / 28316.8
            costo_calculado = pies_c * st.session_state.tarifas['mia_m']
            detalle_u = f"{pies_c:.2f} ft³"
        elif o_in == "Madrid":
            costo_calculado = p_mayor_kg * st.session_state.tarifas['mad']
            detalle_u = f"{p_mayor_kg:.2f} kg"
        else: # Miami Aéreo
            libras = p_mayor_kg * 2.20462
            costo_calculado = libras * st.session_state.tarifas['mia_a']
            detalle_u = f"{libras:.2f} lb"

        # APLICACIÓN DE REGLA DE MÍNIMO (BLOQUE FINAL)
        if costo_calculado < 25.0:
            total_final = 25.0
            st.warning(f"Cálculo técnico: ${costo_calculado:.2f}. Se aplica TARIFA MÍNIMA DE $25.00")
        else:
            total_final = costo_calculado
            
        st.success(f"Dato Facturable: {detalle_u} | TOTAL DDP: ${total_final:.2f}")
