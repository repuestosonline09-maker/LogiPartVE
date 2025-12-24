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
with col1: v_in = st.text_input("Vehículo / Modelo", key=f"v_{st.session_state.count}")
with col2: r_in = st.text_input("Nombre del Repuesto", key=f"r_{st.session_state.count}")
with col3: n_in = st.text_input("Número de Parte", key=f"n_{st.session_state.count}")
with col4: o_in = st.selectbox("Origen", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")
with col5: t_in = st.selectbox("Envío", ["Aéreo", "Marítimo"], key=f"t_{st.session_state.count}")

# 5. MOTOR DE INTELIGENCIA (EL EXPERTO AUTOMOTRIZ DEFINITIVO)
if st.button("🚀 GENERAR ANÁLISIS Y COTIZACIÓN PROFESIONAL", type="primary", use_container_width=True):
    if v_in and r_in and n_in:
        if o_in == "Madrid" and t_in == "Marítimo":
            st.error("⚠️ Error: Madrid solo permite envíos Aéreos.")
            st.stop()

        prompt = f"""
        ACTÚA COMO EL EXPERTO MÁXIMO EN AUTOPARTES Y LOGÍSTICA DDP. 
        Tu marca es LogiPartVE. Tienes conocimiento total de catálogos OEM, números de parte, sustitutos (superseded) y terminología técnica en cualquier idioma.

        DATOS A VALIDAR:
        - Vehículo: {v_in}
        - Repuesto escrito por usuario: {r_in}
        - Número de Parte: {n_in}
        - Ruta: {o_in} vía {t_in}
        - Tarifas: {st.session_state.tarifas}

        TAREA 1: VALIDACIÓN TÉCNICA DE EXPERTO:
        - Analiza si el N° de parte ({n_in}) corresponde realmente al repuesto y al vehículo ({v_in}).
        - Si el número es viejo, indica el número actualizado. 
        - Si el nombre está en otro idioma o es ambiguo, clarifica qué pieza es exactamente.
        - ¡Sé un asesor! Dale seguridad al cliente de que está comprando la pieza correcta.

        TAREA 2: LOGÍSTICA AUTÓNOMA (NO PIDAS DATOS):
        - Define TÚ las medidas (cm) y peso (kg) del repuesto con su EMPAQUE REFORZADO.
        - Calcula Peso Volumétrico (LxAnxAl/5000). Usa el MAYOR entre Real y Volumétrico.
        - MIAMI AÉREO: Multiplica Libras (kg x 2.20462) por {st.session_state.tarifas['mia_a']}.
        - MADRID AÉREO: Multiplica Kilos por {st.session_state.tarifas['mad']}.
        - MIAMI MARÍTIMO: Multiplica Pies Cúbicos (cm3/28316.8) por {st.session_state.tarifas['mia_m']}.

        TAREA 3: REGLA DE ORO DEL MÍNIMO:
        - Si el costo total calculado es MENOR a $25.00 USD, establece el total en $25.00 USD.
        - Indica obligatoriamente: "⚠️ Se aplica tarifa mínima de envío ($25.00)".

        RESULTADO (ESTILO PROFESIONAL Y DIRECTO):
        - Confirmación técnica y de compatibilidad.
        - Detalles del empaque reforzado estimado.
        - COSTO TOTAL DDP: $XX.XX USD (Puerta a puerta, todo incluido).
        """
        
        with st.spinner('Validando compatibilidad técnica y calculando logística...'):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
                if res.status_code == 200:
                    st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
                    st.balloons()
                else: st.error("Error en respuesta de IA.")
            except: st.error("Error de conexión.")
    else: st.warning("⚠️ Complete todos los campos.")

if st.session_state.resultado_ia:
    st.info(st.session_state.resultado_ia)
    if st.button("🗑️ NUEVA CONSULTA", use_container_width=True):
        st.session_state.count += 1
        st.session_state.resultado_ia = ""
        st.rerun()

st.markdown("---")

# 7. CALCULADORA MANUAL (MANTIENE LA PRECISIÓN LOGRADA)
with st.expander("📊 CALCULADORA MANUAL"):
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1: l_cm = st.number_input("Largo (cm)", min_value=0.0)
    with mc2: an_cm = st.number_input("Ancho (cm)", min_value=0.0)
    with mc3: al_cm = st.number_input("Alto (cm)", min_value=0.0)
    with mc4: p_kg_in = st.number_input("Peso Real (kg)", min_value=0.0)
    
    if st.button("🧮 CALCULAR MANUALMENTE"):
        vol_cm3 = l_cm * an_cm * al_cm
        p_vol = vol_cm3 / 5000
        p_mayor_kg = max(p_kg_in, p_vol)
        
        if o_in == "Miami" and t_in == "Marítimo":
            unit_val = vol_cm3 / 28316.8
            costo = unit_val * st.session_state.tarifas['mia_m']
            label = f"{unit_val:.2f} ft³"
        elif o_in == "Madrid":
            costo = p_mayor_kg * st.session_state.tarifas['mad']
            label = f"{p_mayor_kg:.2f} kg"
        else: # Miami Aéreo
            unit_val = p_mayor_kg * 2.20462
            costo = unit_val * st.session_state.tarifas['mia_a']
            label = f"{unit_val:.2f} lb"

        if costo < 25.0:
            st.warning(f"Cálculo: ${costo:.2f}. Se aplica TARIFA MÍNIMA DE $25.00")
            costo = 25.0
            
        st.success(f"Dato Facturable: {label} | TOTAL DDP: ${costo:.2f}")
