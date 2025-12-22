import streamlit as st
import requests
import json

# 1. Configuración y Secretos (Sin cambios para proteger ADN)
st.set_page_config(page_title="LogiPartVE Pro", layout="wide", page_icon="✈️")

try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASS_ADMIN = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("Configura los Secrets.")
    st.stop()

if 'resultado_ia' not in st.session_state: st.session_state.resultado_ia = ""
if 'count' not in st.session_state: st.session_state.count = 0
if 'tarifas' not in st.session_state: st.session_state.tarifas = {"mia_a": 9.0, "mia_m": 40.0, "mad": 20.0}

# 2. CSS Compacto
st.markdown("""
    <style>
    .report-container { padding: 15px; border-radius: 10px; border: 2px solid #007bff; background-color: #ffffff; font-size: 14px; }
    .manual-table { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border: 1px solid #d1d5db; }
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar (Admin)
with st.sidebar:
    check_pass = st.text_input("Admin", type="password")
    if check_pass == PASS_ADMIN:
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo ($/lb)", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo ($/ft³)", value=st.session_state.tarifas["mia_m"])
        st.session_state.tarifas["mad"] = st.number_input("MAD Aéreo ($/kg)", value=st.session_state.tarifas["mad"])

# 4. Encabezado con Iconos
st.title("✈️🚢 LogiPartVE AI: Cotizador Puerta a Puerta")

# 5. Formulario Principal
with st.container():
    c1, c2, c3, c4, c5 = st.columns([2.5, 2, 2, 1, 1])
    with c1: v_in = st.text_input("Vehículo (Marca, Mod, Año, Cil)", key=f"v_{st.session_state.count}")
    with c2: r_in = st.text_input("Repuesto", key=f"r_{st.session_state.count}")
    with c3: n_in = st.text_input("N° Parte", key=f"n_{st.session_state.count}")
    with c4: o_in = st.selectbox("Origen", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")
    with c5: t_in = st.selectbox("Envío", ["Aéreo", "Marítimo"], key=f"t_{st.session_state.count}")

# 6. Lógica de IA con Regla de Peso Mayor (Volumétrico vs Real)
if st.button("🚀 PROCESAR COTIZACIÓN TÉCNICA", type="primary"):
    if v_in and r_in and n_in:
        try:
            url_res = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}").json()
            model_name = [m['name'] for m in url_res.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])][0]
            url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={API_KEY}"

            prompt = f"""
            ERES LOGIPARTVE. EXPERTO LOGÍSTICO INTERNACIONAL. DESTINO VENEZUELA.
            1. VERIFICA: N° {n_in} para {r_in} en {v_in}. Reporta 'ERROR TÉCNICO' si no coincide.
            2. REGLA DE COBRO AÉREO: Debes comparar el PESO REAL estimado vs el PESO VOLUMÉTRICO estimado (L*A*A/166 para lb o /5000 para kg).
               SIEMPRE COTIZA BASADO EN EL VALOR MÁS ALTO.
            3. SOBREDIMENSIÓN: Añade +20% al volumen/peso estimado por empaque reforzado.
            4. TARIFAS: MIA Aéreo ${st.session_state.tarifas['mia_a']}/lb, Mar ${st.session_state.tarifas['mia_m']}/ft³. MAD Aéreo ${st.session_state.tarifas['mad']}/kg.
            5. REGLA MÍNIMO: Si Total Aéreo < $25, advertir 'TARIFA MÍNIMA $25'.
            """
            with st.spinner('Verificando y Calculando con Regla Internacional...'):
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
        except: st.error("Error de conexión.")
    else: st.warning("Complete todos los campos.")

# 7. Resultados
if st.session_state.resultado_ia:
    if "TARIFA MÍNIMA $25" in st.session_state.resultado_ia.upper(): st.warning("⚠️ Tarifa Mínima Aplicable.")
    st.markdown(f'<div class="report-container">{st.session_state.resultado_ia}</div>', unsafe_allow_html=True)
    if st.button("🗑️ LIMPIAR"):
        st.session_state.count += 1
        st.session_state.resultado_ia = ""
        st.rerun()

# 8. TABLA MANUAL CON REGLA DE PESO VOLUMÉTRICO
st.markdown('<div class="manual-table">', unsafe_allow_html=True)
st.markdown("### 📊 Tabla Manual (Regla Internacional de Peso Volumétrico)")
mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
with mc1: l_cm = st.number_input("Largo (cm)", min_value=0.0, key="ml")
with mc2: an_cm = st.number_input("Ancho (cm)", min_value=0.0, key="man")
with mc3: al_cm = st.number_input("Alto (cm)", min_value=0.0, key="mal")
with mc4: p_kg = st.number_input("Peso Real (kg)", min_value=0.0, key="mp")
with mc5: m_origen = st.selectbox("Origen", ["Miami", "Madrid"], key="mo")
with mc6: m_tipo = st.selectbox("Tipo", ["Aéreo", "Marítimo"], key="mt")

if st.button("🧮 CALCULAR"):
    if m_tipo == "Aéreo":
        # Cálculo de Peso Volumétrico en KG
        p_vol_kg = (l_cm * an_cm * al_cm) / 5000
        # Seleccionar el mayor
        p_final_kg = max(p_kg, p_vol_kg)
        
        if m_origen == "Miami":
            p_final_lb = p_final_kg * 2.20462
            costo = max(p_final_lb * st.session_state.tarifas["mia_a"], 25.0)
            st.info(f"Peso Real: {p_kg:.2f}kg | Peso Vol: {p_vol_kg:.2f}kg. Cobrado por: {p_final_kg:.2f}kg")
        else:
            costo = max(p_final_kg * st.session_state.tarifas["mad"], 25.0)
            st.info(f"Peso Real: {p_kg:.2f}kg | Peso Vol: {p_vol_kg:.2f}kg. Cobrado por: {p_final_kg:.2f}kg")
        
        st.success(f"**Costo Puerta a Puerta: ${costo:.2f} USD**")
    else: # Marítimo
        ft3 = (l_cm * an_cm * al_cm) / 28316.8
        st.success(f"**Costo Marítimo: ${(ft3 * st.session_state.tarifas['mia_m']):.2f} USD**")
st.markdown('</div>', unsafe_allow_html=True)
