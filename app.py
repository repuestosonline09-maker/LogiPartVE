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

# 6. Lógica de IA con Nivel de Pago (v1beta para máxima compatibilidad)
if st.button("🚀 GENERAR ANÁLISIS Y COTIZACIÓN", type="primary"):
    if v_in and r_in and n_in:
        # Volvemos a la versión que te funcionaba (v1beta) pero con el modelo Flash completo
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        
        prompt = f"""
        EXPERTO LOGÍSTICO LogiPartVE. 
        1. TÉCNICO: Referencia {n_in} para {r_in} ({v_in}). Usa tu conocimiento de medidas/pesos Mopar/OEM.
        2. COSTOS {o_in.upper()}: Peso mayor (Real vs Vol + 20%). Tarifas: MIA Aé ${st.session_state.tarifas['mia_a']}, Mar ${st.session_state.tarifas['mia_m']} | MAD Aé ${st.session_state.tarifas['mad']}. Mínimo $25.
        3. ALERTAS (DETALLADO): Noticias hoy Diciembre 2025 sobre ruta {o_in} a Venezuela (Aduanas/Clima).
        """

        with st.spinner('Analizando con prioridad de pago...'):
            try:
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                
                if res.status_code == 200:
                    st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
                else:
                    # Si falla el principal, intentamos con el pro como respaldo
                    url_back = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={API_KEY}"
                    res_back = requests.post(url_back, json={"contents": [{"parts": [{"text": prompt}]}]})
                    if res_back.status_code == 200:
                        st.session_state.resultado_ia = res_back.json()['candidates'][0]['content']['parts'][0]['text']
                    else:
                        st.error(f"Error técnico: {res_back.status_code}. Google aún está procesando tu activación de pago.")
            except Exception as e:
                st.error(f"Error de conexión: {str(e)}")
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

# 8. TABLA MANUAL
st.markdown('<div class="manual-table">', unsafe_allow_html=True)
st.markdown("### 📊 Validación Manual")
mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
with mc1: l_cm = st.number_input("Largo (cm)", min_value=0.0, key="ml_last")
with mc2: an_cm = st.number_input("Ancho (cm)", min_value=0.0, key="man_last")
with mc3: al_cm = st.number_input("Alto (cm)", min_value=0.0, key="mal_last")
with mc4: p_kg = st.number_input("Peso (kg)", min_value=0.0, key="mp_last")
with mc5: m_origen = st.selectbox("Origen", ["Miami", "Madrid"], key="mo_last")
with mc6: m_tipo = st.selectbox("Tipo", ["Aéreo", "Marítimo"], key="mt_last")

if st.button("🧮 CALCULAR MANUAL"):
    p_vol_kg = (l_cm * an_cm * al_cm) / 5000
    p_final_kg = max(p_kg, p_vol_kg)
    if m_tipo == "Aéreo":
        factor = 2.20462 if m_origen == "Miami" else 1.0
        tarifa = st.session_state.tarifas["mia_a"] if m_origen == "Miami" else st.session_state.tarifas["mad"]
        costo = max((p_final_kg * factor) * tarifa, 25.0)
    else:
        ft3 = (l_cm * an_cm * al_cm) / 28316.8
        costo = ft3 * st.session_state.tarifas["mia_m"]
    st.success(f"**Costo: ${costo:.2f} USD**")
st.markdown('</div>', unsafe_allow_html=True)
