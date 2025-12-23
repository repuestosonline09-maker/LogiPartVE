import streamlit as st
import requests
import json

# 1. CONFIGURACIÓN PROFESIONAL
st.set_page_config(page_title="LogiPartVE Pro", layout="wide", page_icon="✈️")

# Carga de Secretos
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASS_ADMIN = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("⚠️ Error crítico: Configure 'Secrets' en Streamlit.")
    st.stop()

# ESTADOS DE SESIÓN
if 'resultado_ia' not in st.session_state: st.session_state.resultado_ia = ""
if 'count' not in st.session_state: st.session_state.count = 0
if 'tarifas' not in st.session_state: st.session_state.tarifas = {"mia_a": 9.0, "mia_m": 40.0, "mad": 20.0}

# 2. BARRA LATERAL (ADMIN)
with st.sidebar:
    st.header("⚙️ Configuración Admin")
    check_pass = st.text_input("Contraseña", type="password")
    if check_pass == PASS_ADMIN:
        st.success("Acceso Admin Activo")
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo ($/lb)", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo ($/ft³)", value=st.session_state.tarifas["mia_m"])
        st.session_state.tarifas["mad"] = st.number_input("MAD Aéreo ($/kg)", value=st.session_state.tarifas["mad"])

# 3. INTERFAZ PRINCIPAL
st.title("LogiPartVE: Inteligencia Automotriz DDP")
st.markdown("---")

col1, col2, col3, col4, col5 = st.columns([2.5, 2, 2, 1.5, 1.5])
with col1: v_in = st.text_input("Vehículo / Modelo", key=f"v_{st.session_state.count}")
with col2: r_in = st.text_input("Nombre del Repuesto", key=f"r_{st.session_state.count}")
with col3: n_in = st.text_input("Número de Parte", key=f"n_{st.session_state.count}")
with col4: o_in = st.selectbox("Origen", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")
with col5: t_in = st.selectbox("Envío", ["Aéreo", "Marítimo"], key=f"t_{st.session_state.count}")

# 4. PROMPT MAESTRO (TRIANGULACIÓN Y EMPAQUES REFORZADOS)
if st.button("🚀 GENERAR ANÁLISIS Y COTIZACIÓN PROFESIONAL", type="primary"):
    if v_in and r_in and n_in:
        modelos_a_probar = ["gemini-2.0-flash", "gemini-1.5-pro"]
        
        prompt = f"""
        ACTÚA COMO UN EXPERTO EN REPUESTOS AUTOMOTRICES Y LOGÍSTICA DDP.
        
        DATOS DE ENTRADA:
        - Vehículo: {v_in}
        - Repuesto: {r_in}
        - N° Parte: {n_in}
        - Ruta: {o_in} hacia Venezuela via {t_in}.
        - Tarifas base: {st.session_state.tarifas}

        TU TAREA (SÉ DIRECTO Y RESUMIDO):
        1. TRIANGULACIÓN: Verifica si el N° de parte {n_in} corresponde al {r_in} para un {v_in}. Indica sustitutos o actualizaciones si existen.
        2. DIMENSIONES Y PROTECCIÓN: Estima el peso y medidas REALES de la pieza. Luego, calcula el sobre-empaque REFORZADO necesario para protección internacional (incrementa medidas para el cálculo).
        3. CÁLCULO DDP: Basado en el peso/volumen del empaque REFORZADO y las tarifas de {o_in} ({t_in}), emite la cotización final.
        4. ADUANA: Alertas específicas para esta pieza en Venezuela (DDP).
        
        FORMATO DE SALIDA:
        - Informe Técnico (Breve).
        - Logística y Empaque (Medidas estimadas del empaque reforzado).
        - Cotización Final USD (Basada en empaque reforzado).
        """

        with st.spinner('Triangulando información y calculando empaques...'):
            for m_name in modelos_a_probar:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m_name}:generateContent?key={API_KEY}"
                try:
                    res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
                    if res.status_code == 200:
                        st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
                        st.balloons()
                        break
                except: continue
    else:
        st.warning("Por favor, rellene todos los campos para triangular la información.")

# 5. RESULTADOS
if st.session_state.resultado_ia:
    st.markdown("### 📝 Análisis Técnico y Cotización DDP")
    st.info(st.session_state.resultado_ia)
    
    if st.button("🗑️ NUEVA CONSULTA"):
        st.session_state.count += 1
        st.session_state.resultado_ia = ""
        st.rerun()

# 6. CALCULADORA MANUAL (RESTAURADA)
st.markdown("---")
with st.expander("📊 CALCULADORA MANUAL DE RESPALDO"):
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1: l_cm = st.number_input("Largo (cm)", min_value=0.0)
    with mc2: an_cm = st.number_input("Ancho (cm)", min_value=0.0)
    with mc3: al_cm = st.number_input("Alto (cm)", min_value=0.0)
    with mc4: p_kg = st.number_input("Peso (kg)", min_value=0.0)
    if st.button("🧮 CALCULAR"):
        p_v = (l_cm * an_cm * al_cm) / 5000
        p_f = max(p_kg, p_v)
        st.write(f"Peso a facturar: {p_f:.2f} kg/lb | Costo: ${p_f * st.session_state.tarifas['mia_a']:.2f}")
