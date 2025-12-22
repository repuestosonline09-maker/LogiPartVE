import streamlit as st
import requests
import json
import time

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="LogiPartVE Pro", layout="wide", page_icon="✈️")

# Carga de Secretos
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASS_ADMIN = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("⚠️ Error: Configure 'Secrets' en Streamlit.")
    st.stop()

# ESTADOS DE SESIÓN
if 'resultado_ia' not in st.session_state: st.session_state.resultado_ia = ""
if 'count' not in st.session_state: st.session_state.count = 0
if 'tarifas' not in st.session_state: st.session_state.tarifas = {"mia_a": 9.0, "mia_m": 40.0, "mad": 20.0}

# 2. DISEÑO CSS
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    .report-container { 
        padding: 20px; border-radius: 10px; background-color: #ffffff; 
        border: 2px solid #007bff; font-size: 15px; line-height: 1.5; color: #1e1e1e;
    }
    .manual-table { background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-top: 15px; border: 1px solid #dee2e6; }
    .stButton>button {width: 100%; height: 3em; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# 3. SIDEBAR (ADMIN)
with st.sidebar:
    st.header("⚙️ Configuración")
    check_pass = st.text_input("Contraseña Admin", type="password")
    if check_pass == PASS_ADMIN:
        st.success("Acceso concedido")
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo ($/lb)", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo ($/ft³)", value=st.session_state.tarifas["mia_m"])
        st.session_state.tarifas["mad"] = st.number_input("MAD Aéreo ($/kg)", value=st.session_state.tarifas["mad"])
    else:
        st.info("Ingrese clave para editar tarifas.")

# 4. ENCABEZADO
c1, c2 = st.columns([1, 6])
with c1: st.image("https://cdn-icons-png.flaticon.com/512/2208/2208233.png", width=70) 
with c2: st.title("LogiPartVE: Gestión Experta DDP")

# 5. FORMULARIO
with st.container():
    col1, col2, col3, col4, col5 = st.columns([2.5, 2, 2, 1.5, 1.5])
    with col1: v_in = st.text_input("Vehículo / Modelo", key=f"v_{st.session_state.count}")
    with col2: r_in = st.text_input("Nombre del Repuesto", key=f"r_{st.session_state.count}")
    with col3: n_in = st.text_input("Número de Parte", key=f"n_{st.session_state.count}")
    with col4: o_in = st.selectbox("Origen", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")
    with col5: t_in = st.selectbox("Tipo de Envío", ["Aéreo", "Marítimo"], key=f"t_{st.session_state.count}")

# 6. LÓGICA DE IA (NIVEL DE PAGO 1)
if st.button("🚀 GENERAR ANÁLISIS Y COTIZACIÓN PROFESIONAL", type="primary"):
    if v_in and r_in and n_in:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        url_back = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={API_KEY}"
        
        prompt = f"Experto LogiPartVE. Analiza {r_in} para {v_in} ref {n_in}. Origen {o_in}. Diciembre 2025."

        with st.spinner('Procesando con prioridad de pago...'):
            try:
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
                if res.status_code == 200:
                    st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
                else:
                    res_back = requests.post(url_back, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
                    if res_back.status_code == 200:
                        st.session_state.resultado_ia = res_back.json()['candidates'][0]['content']['parts'][0]['text']
                    else:
                        st.error(f"Error de API: {res_back.status_code}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Faltan datos.")

# 7. RESULTADOS
if st.session_state.resultado_ia:
    st.markdown(f'<div class="report-container">{st.session_state.resultado_ia}</div>', unsafe_allow_html=True)
    if st.button("🗑️ LIMPIAR"):
        st.session_state.count += 1
        st.session_state.resultado_ia = ""
        st.rerun()

# 8. CALCULADORA MANUAL (CORREGIDA)
st.markdown('<div class="manual-table">', unsafe_allow_html=True)
st.markdown("### 📊 Validación Manual")
mc1, mc2, mc3, mc4 = st.columns(4)
with mc1: l_cm = st.number_input("Largo (cm)", min_value=0.0)
with mc2: an_cm = st.number_input("Ancho (cm)", min_value=0.0)
with mc3: al_cm = st.number_input("Alto (cm)", min_value=0.0)
with mc4: p_kg = st.number_input("Peso (kg)", min_value=0.0)

if st.button("🧮 CALCULAR COSTO MANUAL"):
    p_vol_kg = (l_cm * an_cm * al_cm) / 5000
    p_final_kg = max(p_kg, p_vol_kg)
    # Ejemplo de cálculo simplificado para evitar errores
    costo_base = p_final_kg * 10.0
    st.success(f"**Costo Estimado: ${costo_base:.2f} USD**")
st.markdown('</div>', unsafe_allow_html=True)
