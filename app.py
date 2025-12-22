import streamlit as st
import requests
import json

# 1. Configuración de página
st.set_page_config(page_title="LogiPartVE Pro", layout="wide", page_icon="✈️")

# Carga de Secretos
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASS_ADMIN = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("Configura los Secrets.")
    st.stop()

# Estados
if 'resultado_ia' not in st.session_state: st.session_state.resultado_ia = ""
if 'count' not in st.session_state: st.session_state.count = 0
if 'tarifas' not in st.session_state: st.session_state.tarifas = {"mia_a": 9.0, "mia_m": 40.0, "mad": 20.0}

# 2. CSS Compacto (Máxima visibilidad)
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    .report-container { 
        padding: 15px; border-radius: 10px; background-color: #ffffff; 
        border: 2px solid #007bff; font-size: 14px; line-height: 1.2;
    }
    .manual-table { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-top: 10px; border: 1px solid #d1d5db; }
    .stButton>button {height: 2.8em;}
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar (Admin)
with st.sidebar:
    check_pass = st.text_input("Admin", type="password")
    if check_pass == PASS_ADMIN:
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo", value=st.session_state.tarifas["mia_m"])
        st.session_state.tarifas["mad"] = st.number_input("MAD Aéreo", value=st.session_state.tarifas["mad"])

# 4. Encabezado
c_logo1, c_logo2 = st.columns([1, 5])
with c_logo1:
    st.image("https://cdn-icons-png.flaticon.com/512/2208/2208233.png", width=60) 
with c_logo2:
    st.title("LogiPartVE: Verificación y Cotización Puerta a Puerta")

# 5. Formulario Principal
with st.container():
    c1, c2, c3, c4, c5 = st.columns([2.5, 2, 2, 1, 1])
    with c1: v_in = st.text_input("Vehículo (Marca, Mod, Año, Cil)", key=f"v_{st.session_state.count}")
    with c2: r_in = st.text_input("Repuesto", key=f"r_{st.session_state.count}")
    with c3: n_in = st.text_input("N° Parte", key=f"n_{st.session_state.count}")
    with c4: o_in = st.selectbox("Origen", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")
    with c5: t_in = st.selectbox("Envío", ["Aéreo", "Marítimo"], key=f"t_{st.session_state.count}")

# 6. Lógica de IA con Verificación Técnica Estricta
if st.button("🚀 PROCESAR COTIZACIÓN TÉCNICA", type="primary"):
    if v_in and r_in and n_in:
        try:
            url_res = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}").json()
            model_name = [m['name'] for m in url_res.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])][0]
            url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={API_KEY}"

            prompt = f"""
            ERES EL EXPERTO TÉCNICO DE LOGIPARTVE. DESTINO SIEMPRE VENEZUELA.
            
            PASO 1 (CRÍTICO): VERIFICACIÓN TÉCNICA.
            Cruza el N° de Parte {n_in} con el Vehículo {v_in} y el Repuesto {r_in}.
            - Si NO coinciden o hay duda, detente. Reporta 'ERROR TÉCNICO', explica la falla y pide corrección al vendedor.
            
            PASO 2 (COTIZACIÓN): Solo si el paso 1 es exitoso.
            - Estima peso/medidas del componente y suma +20% obligatorio (Factor Seguridad).
            - Tarifas de Origen {o_in.upper()} y Envío {t_in.upper()}:
              MIA: Aéreo ${st.session_state.tarifas['mia_a']}/lb, Mar ${st.session_state.tarifas['mia_m']}/ft³.
              MAD: Aéreo ${st.session_state.tarifas['mad']}/kg.
            
            PASO 3 (REGLA DE $25): Si el total Aéreo es < $25, escribe '⚠️ TARIFA MÍNIMA $25'.
            
            SALIDA ULTRA-RESUMIDA:
            1. Estatus Verificación.
            2. Ficha: Peso y Medidas (con +20%).
            3. Costo Total Puerta a Puerta (Solo origen {o_in.upper()}).
            4. Embalaje/Alertas Globales.
            """

            with st.spinner('Verificando compatibilidad técnica...'):
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
        except: st.error("Error de conexión.")
    else: st.warning("Complete todos los campos.")

# 7. Resultados y Limpieza
if st.session_state.resultado_ia:
    if "ERROR TÉCNICO" in st.session_state.resultado_ia.upper():
        st.error("⚠️ Inconsistencia Detectada en los Datos")
    elif "TARIFA MÍNIMA $25" in st.session_state.resultado_ia.upper():
        st.warning("ℹ️ Aplica Tarifa Mínima")
    
    st.markdown(f'<div class="report-container">{st.session_state.resultado_ia}</div>', unsafe_allow_html=True)
    
    c_dw, c_cl = st.columns([5, 1])
    with c_dw: st.download_button("📥 Descargar Cotización", st.session_state.resultado_ia, file_name="cotizacion_logipartve.txt")
    with c_cl: 
        if st.button("🗑️ LIMPIAR"):
            st.session_state.count += 1
            st.session_state.resultado_ia = ""
            st.rerun()

# 8. TABLA MANUAL (Mantenida sin cambios para estabilidad)
st.markdown('<div class="manual-table">', unsafe_allow_html=True)
st.markdown("### 📊 Tabla de Validación Manual")
mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
with mc1: l_cm = st.number_input("Largo (cm)", min_value=0.0, key="ml")
with mc2: an_cm = st.number_input("Ancho (cm)", min_value=0.0, key="man")
with mc3: al_cm = st.number_input("Alto (cm)", min_value=0.0, key="mal")
with mc4: p_kg = st.number_input("Peso (kg)", min_value=0.0, key="mp")
with mc5: m_origen = st.selectbox("Origen", ["Miami", "Madrid"], key="mo")
with mc6: m_tipo = st.selectbox("Tipo", ["Aéreo", "Marítimo"], key="mt")

if st.button("🧮 CALCULAR MANUAL"):
    p_lb = p_kg * 2.20462
    ft3 = (l_cm * an_cm * al_cm) / 28316.8
    costo = 0.0
    if m_origen == "Miami":
        costo = max(p_lb * st.session_state.tarifas["mia_a"], 25.0) if m_tipo == "Aéreo" else ft3 * st.session_state.tarifas["mia_m"]
    else:
        costo = max(p_kg * st.session_state.tarifas["mad"], 25.0) if m_tipo == "Aéreo" else 0
        if m_tipo == "Marítimo": st.error("Madrid solo Aéreo")
    
    if costo > 0: st.success(f"**Costo Manual {m_origen}: ${costo:.2f} USD**")
st.markdown('</div>', unsafe_allow_html=True)
