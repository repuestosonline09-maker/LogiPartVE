import streamlit as st
import requests
import json

# 1. Configuración de página
st.set_page_config(page_title="LogiPartVE Pro", layout="wide", page_icon="✈️")

# Carga de Secretos (ADN Protegido)
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

# 2. CSS Ultra-Compacto
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
    st.title("LogiPartVE: Verificación, Cotización y Alertas en Tiempo Real")

# 5. Formulario Principal
with st.container():
    c1, c2, c3, c4, c5 = st.columns([2.5, 2, 2, 1.2, 1.2])
    with c1: v_in = st.text_input("Vehículo (Marca, Mod, Año, Cil)", key=f"v_{st.session_state.count}")
    with c2: r_in = st.text_input("Repuesto", key=f"r_{st.session_state.count}")
    with c3: n_in = st.text_input("N° Parte", key=f"n_{st.session_state.count}")
    with c4: o_in = st.selectbox("Origen", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")
    with c5: t_in = st.selectbox("Envío", ["Aéreo", "Marítimo"], key=f"t_{st.session_state.count}")

# 6. Lógica de IA (Verificación + Peso Volumétrico + Monitoreo de Noticias)
if st.button("🚀 PROCESAR OPERACIÓN", type="primary"):
    if v_in and r_in and n_in:
        try:
            url_res = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}").json()
            model_name = [m['name'] for m in url_res.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])][0]
            url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={API_KEY}"

            prompt = f"""
            ERES LOGIPARTVE. EXPERTO TÉCNICO Y ANALISTA DE RIESGO LOGÍSTICO. 
            DESTINO: VENEZUELA (PUERTA A PUERTA).

            1. VERIFICACIÓN: Cruza N° {n_in} con {r_in} y {v_in}. Reporta 'ERROR TÉCNICO' si hay inconsistencia.
            
            2. CÁLCULO LOGÍSTICO ({o_in.upper()} - {t_in.upper()}): 
               - Estima dimensiones reales + 20% de seguridad.
               - Aplica Regla Internacional: El cobro se basa en el mayor entre PESO REAL y PESO VOLUMÉTRICO.
               - Tarifas: MIA Aéreo ${st.session_state.tarifas['mia_a']}, Mar ${st.session_state.tarifas['mia_m']} | MAD Aéreo ${st.session_state.tarifas['mad']}.
               - REGLA MÍNIMO: Si Aéreo < $25, advertir 'TARIFA MÍNIMA $25'.

            3. MONITOREO DE NOTICIAS Y ALERTAS (CRÍTICO): 
               - Analiza información actual (hoy diciembre 2025) sobre huelgas portuarias, problemas climáticos en el Caribe/Atlántico, retrasos en aduanas venezolanas o cualquier noticia que afecte la ruta {o_in} ➔ Venezuela.
               - Si detectas un riesgo, descríbelo brevemente como 'ALERTA DE RUTA'.

            SALIDA: Resultado Verificación, Ficha (con +20% y comparativa de peso), Costo Final y sección de Alertas/Noticias.
            """

            with st.spinner('Auditando compatibilidad y monitoreando noticias globales...'):
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
        except: st.error("Error de comunicación.")
    else: st.warning("Complete todos los campos.")

# 7. Resultados y Limpieza
if st.session_state.resultado_ia:
    # Mostrar alertas visuales según el contenido
    if "ERROR TÉCNICO" in st.session_state.resultado_ia.upper(): st.error("⚠️ Inconsistencia Técnica")
    if "ALERTA" in st.session_state.resultado_ia.upper(): st.warning("📢 Alerta Logística Detectada")
    
    st.markdown(f'<div class="report-container">{st.session_state.resultado_ia}</div>', unsafe_allow_html=True)
    
    c_dw, c_cl = st.columns([5, 1])
    with c_dw: st.download_button("📥 Descargar", st.session_state.resultado_ia, file_name="cotizacion.txt")
    with c_cl: 
        if st.button("🗑️ LIMPIAR"):
            st.session_state.count += 1
            st.session_state.resultado_ia = ""
            st.rerun()

# 8. TABLA MANUAL (Sin cambios para estabilidad)
st.markdown('<div class="manual-table">', unsafe_allow_html=True)
st.markdown("### 📊 Tabla de Validación Manual (CM / KG)")
mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
with mc1: l_cm = st.number_input("Largo (cm)", min_value=0.0, key="ml")
with mc2: an_cm = st.number_input("Ancho (cm)", min_value=0.0, key="man")
with mc3: al_cm = st.number_input("Alto (cm)", min_value=0.0, key="mal")
with mc4: p_kg = st.number_input("Peso (kg)", min_value=0.0, key="mp")
with mc5: m_origen = st.selectbox("Origen", ["Miami", "Madrid"], key="mo")
with mc6: m_tipo = st.selectbox("Tipo", ["Aéreo", "Marítimo"], key="mt")

if st.button("🧮 CALCULAR MANUAL"):
    if m_tipo == "Aéreo":
        p_vol_kg = (l_cm * an_cm * al_cm) / 5000
        p_final_kg = max(p_kg, p_vol_kg)
        costo = max((p_final_kg * 2.20462 if m_origen == "Miami" else p_final_kg) * (st.session_state.tarifas["mia_a"] if m_origen == "Miami" else st.session_state.tarifas["mad"]), 25.0)
        st.success(f"**Costo {m_origen} ({m_tipo}): ${costo:.2f} USD**")
    else:
        ft3 = (l_cm * an_cm * al_cm) / 28316.8
        st.success(f"**Costo Marítimo MIA: ${(ft3 * st.session_state.tarifas['mia_m']):.2f} USD**")
st.markdown('</div>', unsafe_allow_html=True)
