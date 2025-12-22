import streamlit as st
import requests
import json

# 1. Configuración de página (Mantenida)
st.set_page_config(page_title="LogiPartVE Pro", layout="wide", page_icon="✈️")

# Carga de Secretos (Protegida)
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASS_ADMIN = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("Configura los Secrets.")
    st.stop()

# Estados (Preservados)
if 'resultado_ia' not in st.session_state: st.session_state.resultado_ia = ""
if 'count' not in st.session_state: st.session_state.count = 0
if 'tarifas' not in st.session_state: st.session_state.tarifas = {"mia_a": 9.0, "mia_m": 40.0, "mad": 20.0}

# 2. CSS Compacto (Mantenido y Ajustado)
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    .report-container { 
        padding: 15px; border-radius: 10px; background-color: #f8f9fa; 
        border: 1px solid #007bff; font-size: 14px; line-height: 1.3;
    }
    .manual-table { background-color: #eef4fb; padding: 15px; border-radius: 10px; border: 1px solid #b3d7ff; margin-top: 20px; }
    h1 {margin-bottom: 0px; font-size: 24px;}
    .stButton>button {height: 2.5em; margin-top: 10px;}
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar (Admin - Protegido)
with st.sidebar:
    check_pass = st.text_input("Admin", type="password")
    if check_pass == PASS_ADMIN:
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo", value=st.session_state.tarifas["mia_m"])
        st.session_state.tarifas["mad"] = st.number_input("MAD Aéreo", value=st.session_state.tarifas["mad"])

# 4. Encabezado
c_logo1, c_logo2 = st.columns([1, 5])
with c_logo1:
    st.image("https://cdn-icons-png.flaticon.com/512/2208/2208233.png", width=70) 
with c_logo2:
    st.title("LogiPartVE: Cotizador Puerta a Puerta")

# 5. Formulario Principal (Actualizado con Tipo de Envío)
with st.container():
    c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 1.2, 1.2])
    with c1: v_in = st.text_input("Vehículo", key=f"v_{st.session_state.count}")
    with c2: r_in = st.text_input("Repuesto", key=f"r_{st.session_state.count}")
    with c3: n_in = st.text_input("N° Parte", key=f"n_{st.session_state.count}")
    with c4: o_in = st.selectbox("Origen", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")
    with c5: t_in = st.selectbox("Envío", ["Aéreo", "Marítimo"], key=f"t_{st.session_state.count}")

# 6. Lógica de IA (Protegida)
if st.button("🚀 COTIZAR AHORA", type="primary"):
    if v_in and r_in and n_in:
        try:
            url_res = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}").json()
            model_name = [m['name'] for m in url_res.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])][0]
            url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={API_KEY}"

            prompt = f"""
            ERES LOGIPARTVE. Resumen Ejecutivo Puerta a Puerta.
            PRODUCTO: {n_in} para {r_in} ({v_in}).
            REGLA ESTRICTA: Solo calcula origen {o_in.upper()} y modo {t_in.upper()}. No menciones otros.
            
            CÁLCULO:
            1. Estima peso/medidas y suma +20% (Seguridad).
            2. TARIFAS: Miami (Aéreo ${st.session_state.tarifas['mia_a']}/lb, Mar ${st.session_state.tarifas['mia_m']}/ft³). Madrid (Aéreo ${st.session_state.tarifas['mad']}/kg).
            3. MINIMO: Si Aéreo < $25, advertir 'TARIFA MÍNIMA $25'.
            
            SALIDA: Verificación Técnica, Ficha (con +20%) y Costo Total Puerta a Puerta.
            """

            with st.spinner('Procesando...'):
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
        except: st.error("Error de conexión.")
    else: st.warning("Faltan datos.")

# 7. Resultados de IA y Botón Limpiar (Protegido)
if st.session_state.resultado_ia:
    if "TARIFA MÍNIMA $25" in st.session_state.resultado_ia.upper():
        st.warning("⚠️ Tarifa Mínima de $25 aplicable.")
    st.markdown(f'<div class="report-container">{st.session_state.resultado_ia}</div>', unsafe_allow_html=True)
    if st.button("🗑️ LIMPIAR TODO", key="clear_btn"):
        st.session_state.count += 1
        st.session_state.resultado_ia = ""
        st.rerun()

# 8. NUEVA SECCIÓN: TABLA MANUAL (Independiente)
st.markdown('<div class="manual-table">', unsafe_allow_html=True)
st.subheader("📊 TABLA MANUAL (Cálculo Exacto)")
mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
with mc1: l_cm = st.number_input("Largo (cm)", min_value=0.0)
with mc2: an_cm = st.number_input("Ancho (cm)", min_value=0.0)
with mc3: al_cm = st.number_input("Alto (cm)", min_value=0.0)
with mc4: p_kg = st.number_input("Peso Real (kg)", min_value=0.0)
with mc5: m_origen = st.selectbox("Origen", ["Miami", "Madrid"], key="man_orig")
with mc6: m_tipo = st.selectbox("Tipo", ["Aéreo", "Marítimo"], key="man_tipo")

if st.button("🧮 CALCULAR COSTO MANUAL"):
    # Conversiones
    p_lb = p_kg * 2.20462
    pies_cubicos = (l_cm * an_cm * al_cm) / 28316.8 # CM3 a FT3
    
    costo_man = 0.0
    if m_origen == "Miami":
        if m_tipo == "Aéreo":
            costo_man = max(p_lb * st.session_state.tarifas["mia_a"], 25.0)
        else:
            costo_man = pies_cubicos * st.session_state.tarifas["mia_m"]
    else: # Madrid
        if m_tipo == "Aéreo":
            costo_man = max(p_kg * st.session_state.tarifas["mad"], 25.0)
        else:
            st.error("Madrid solo dispone de envío Aéreo.")
    
    if costo_man > 0:
        st.success(f"**Resultado Manual {m_origen} ({m_tipo}): ${costo_man:.2f} USD** (Puerta a Puerta)")
st.markdown('</div>', unsafe_allow_html=True)

st.caption(f"v4.6 | LogiPartVE | Tarifas actuales: MIA A:{st.session_state.tarifas['mia_a']} M:{st.session_state.tarifas['mia_m']} | MAD:{st.session_state.tarifas['mad']}")
