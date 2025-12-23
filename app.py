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
    st.error("⚠️ Error crítico: No se encontraron los Secrets en Streamlit Cloud.")
    st.stop()

# ESTADOS DE SESIÓN
if 'resultado_ia' not in st.session_state: st.session_state.resultado_ia = ""
if 'count' not in st.session_state: st.session_state.count = 0
if 'tarifas' not in st.session_state: st.session_state.tarifas = {"mia_a": 9.0, "mia_m": 40.0, "mad": 20.0}

# 2. BLOQUE DE VERIFICACIÓN TÉCNICA (SIDEBAR)
with st.sidebar:
    st.header("🔍 Diagnóstico de Conexión")
    if st.button("VERIFICAR LLAVE ACTIVA"):
        llave_actual = st.secrets["GOOGLE_API_KEY"]
        st.write(f"Llave detectada: `...{llave_actual[-4:]}`")
        if llave_actual.endswith("MYTA"):
            st.success("✅ CONEXIÓN CORRECTA: Estás usando la llave de PAGO (MYTA).")
        else:
            st.error("❌ ERROR: La llave en Secrets no termina en MYTA.")
    
    st.markdown("---")
    st.header("⚙️ Configuración Admin")
    check_pass = st.text_input("Contraseña", type="password")
    if check_pass == PASS_ADMIN:
        st.success("Acceso Admin Activo")
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo ($/lb)", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo ($/ft³)", value=st.session_state.tarifas["mia_m"])
        st.session_state.tarifas["mad"] = st.number_input("MAD Aéreo ($/kg)", value=st.session_state.tarifas["mad"])

# 3. INTERFAZ PRINCIPAL
st.title("LogiPartVE: Gestión Experta DDP")
st.markdown("---")

with st.container():
    col1, col2, col3, col4, col5 = st.columns([2.5, 2, 2, 1.5, 1.5])
    with col1: v_in = st.text_input("Vehículo / Modelo", key=f"v_{st.session_state.count}")
    with col2: r_in = st.text_input("Nombre del Repuesto", key=f"r_{st.session_state.count}")
    with col3: n_in = st.text_input("Número de Parte", key=f"n_{st.session_state.count}")
    with col4: o_in = st.selectbox("Origen", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")
    with col5: t_in = st.selectbox("Envío", ["Aéreo", "Marítimo"], key=f"t_{st.session_state.count}")

# 4. LÓGICA DE IA (SISTEMA MULTIMOTOR PARA NIVEL 1 / CRÉDITOS MASIVOS)
if st.button("🚀 GENERAR ANÁLISIS Y COTIZACIÓN PROFESIONAL", type="primary"):
    if v_in and r_in and n_in:
        # Lista de modelos por orden de probabilidad en cuentas premium
        modelos = ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"]
        exito = False
        
        prompt = f"ACTÚA COMO EXPERTO LOGÍSTICO LogiPartVE. Analiza {r_in} ({n_in}) para {v_in}. Origen {o_in}. Tarifas: {st.session_state.tarifas}. Diciembre 2025."

        with st.spinner('Sincronizando con tus créditos de $1.1M...'):
            for m_name in modelos:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m_name}:generateContent?key={API_KEY}"
                try:
                    res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15)
                    if res.status_code == 200:
                        st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
                        st.balloons()
                        exito = True
                        break
                except:
                    continue
            
            if not exito:
                st.error("⚠️ Google está procesando tu nivel de pago. Si persiste, intenta en unos minutos.")
    else:
        st.warning("Por favor, rellene todos los campos.")

# 5. VISUALIZACIÓN DE RESULTADOS
if st.session_state.resultado_ia:
    st.markdown("### 📝 Resultado del Análisis")
    st.info(st.session_state.resultado_ia)
    
    if st.button("🗑️ LIMPIAR FORMULARIO"):
        st.session_state.count += 1
        st.session_state.resultado_ia = ""
        st.rerun()

# 6. CALCULADORA MANUAL
st.markdown("---")
with st.expander("📊 Calculadora Manual de Costos"):
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1: l_cm = st.number_input("Largo (cm)", min_value=0.0)
    with mc2: an_cm = st.number_input("Ancho (cm)", min_value=0.0)
    with mc3: al_cm = st.number_input("Alto (cm)", min_value=0.0)
    with mc4: p_kg = st.number_input("Peso (kg)", min_value=0.0)
    
    if st.button("🧮 CALCULAR MANUALMENTE"):
        p_vol_kg = (l_cm * an_cm * al_cm) / 5000
        p_final_kg = max(p_kg, p_vol_kg)
        costo_est = p_final_kg * st.session_state.tarifas["mia_a"]
        st.success(f"Costo estimado base: ${costo_est:.2f} USD")
