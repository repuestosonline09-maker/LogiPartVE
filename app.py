import streamlit as st
import requests
import json
import time

# 1. Configuración de página
st.set_page_config(page_title="LogiPartVE Pro", layout="wide", page_icon="✈️")

# Carga de Secretos
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASS_ADMIN = st.secrets["ADMIN_PASSWORD"]
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

# 6. Lógica de IA (Usando la URL estable v1 para cuentas de pago)
if st.button("🚀 GENERAR ANÁLISIS Y COTIZACIÓN", type="primary"):
    if v_in and r_in and n_in:
        # URL estable que reconoce tu Nivel de Pago 1
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Experto LogiPartVE. Analiza {r_in} parte {n_in} para {v_in}. Origen {o_in}. Diciembre 2025."
                }]
            }]
        }

        with st.spinner('Analizando con prioridad de pago...'):
            try:
                res = requests.post(url, json=payload)
                if res.status_code == 200:
                    st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
                else:
                    # Si falla el principal, probamos con gemini-pro en v1
                    url_pro = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={API_KEY}"
                    res_pro = requests.post(url_pro, json=payload)
                    if res_pro.status_code == 200:
                        st.session_state.resultado_ia = res_pro.json()['candidates'][0]['content']['parts'][0]['text']
                    else:
                        st.error(f"Error técnico {res_pro.status_code}. Google aún procesa tu pago.")
            except Exception as e:
                st.error(f"Error de conexión: {str(e)}")
    else:
        st.warning("Faltan datos.")

# 7. Resultados
if st.session_state.resultado_ia:
    st.markdown(f'<div class="report-container">{st.session_state.resultado_ia}</div>', unsafe_allow_html=True)
    if st.button("🗑️ LIMPIAR"):
        st.session_state.count += 1
        st.session_state.resultado_ia = ""
        st.rerun()

# 8. Tabla Manual
st.markdown('<div class="manual-table">', unsafe_allow_html=True)
st.markdown("### 📊 Validación Manual")
mc1, mc2, mc3, mc4 = st.columns(4)
with mc1: l_cm = st.number_input("Largo (cm)", min_value=0.0, key="ml_v_final")
with mc2: an_cm = st.number_input("Ancho (cm)", min_value=0.0, key="man_v_final")
with mc3: al_cm = st.number_input("Alto (cm)", min_value=0.0, key="mal_v_final")
with mc4: p_kg = st.number_input("Peso (kg)", min_value=0.0, key="mp_v_final")

if st.button("🧮 CALCULAR MANUAL"):
    p_vol_kg = (l_cm * an_cm * al_cm) / 5000
    p_final_kg = max(p_kg, p_vol_kg)
    costo = p_final_kg * st.session_state.tarifas["mia_a"]
    st.success(f"**Costo: ${costo:.2f} USD**")
st.markdown('</div>', unsafe_allow_html=True)
