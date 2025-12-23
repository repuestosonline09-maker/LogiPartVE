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

# 2. BARRA LATERAL (DIAGNÓSTICO Y ADMIN)
with st.sidebar:
    st.header("🔍 Estatus")
    if st.secrets["GOOGLE_API_KEY"].endswith("MYTA"):
        st.success("Conexión Premium Activa")
    
    st.markdown("---")
    st.header("⚙️ Tarifas")
    check_pass = st.text_input("Contraseña Admin", type="password")
    if check_pass == PASS_ADMIN:
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo ($/lb)", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo ($/ft³)", value=st.session_state.tarifas["mia_m"])

# 3. INTERFAZ DE ENTRADA
st.title("LogiPartVE: Análisis Logístico DDP")
st.markdown("---")

col1, col2, col3, col4, col5 = st.columns([2.5, 2, 2, 1.5, 1.5])
with col1: v_in = st.text_input("Vehículo", key=f"v_{st.session_state.count}")
with col2: r_in = st.text_input("Repuesto", key=f"r_{st.session_state.count}")
with col3: n_in = st.text_input("N° Parte", key=f"n_{st.session_state.count}")
with col4: o_in = st.selectbox("Origen", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")
with col5: t_in = st.selectbox("Envío", ["Aéreo", "Marítimo"], key=f"t_{st.session_state.count}")

# 4. LÓGICA DE INTELIGENCIA LOGÍSTICA (PROMPT RESTAURADO Y RESUMIDO)
if st.button("🚀 GENERAR ANÁLISIS Y COTIZACIÓN", type="primary"):
    if v_in and r_in and n_in:
        modelos = ["gemini-2.0-flash", "gemini-1.5-pro"]
        
        # PROMPT MAESTRO OPTIMIZADO PARA BREVEDAD
        prompt = f"""
        ERES EL EXPERTO LOGÍSTICO DE LOGIPARTVE. 
        OBJETIVO: Análisis técnico y logístico DDP para {r_in} ({n_in}) de {v_in}.
        ORIGEN: {o_in} | ENVÍO: {t_in}.
        TARIFAS ACTUALES: {st.session_state.tarifas}.

        INSTRUCCIONES DE FORMATO (ESTRICTO):
        1. SÉ MUY BREVE Y DIRECTO. No saludes, no des introducciones.
        2. ANÁLISIS TÉCNICO: Confirma si el N° de parte coincide con el vehículo. Menciona peso/dimensiones estimadas.
        3. LOGÍSTICA DDP: Explica brevemente el proceso desde {o_in} a Venezuela.
        4. ALERTA ADUANA: Indica si el repuesto tiene restricciones o requiere permisos especiales.
        5. RESUMEN DE COSTOS: Da un estimado final basado en las tarifas provistas.
        Usa viñetas. Máximo 150 palabras.
        """

        with st.spinner('Analizando...'):
            for m_name in modelos:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m_name}:generateContent?key={API_KEY}"
                try:
                    res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15)
                    if res.status_code == 200:
                        st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
                        st.balloons()
                        break
                except: continue
    else:
        st.warning("Complete todos los campos.")

# 5. RESULTADOS
if st.session_state.resultado_ia:
    st.markdown("### 📝 Resultado Consolidado")
    st.info(st.session_state.resultado_ia)
    
    if st.button("🗑️ NUEVA CONSULTA"):
        st.session_state.count += 1
        st.session_state.resultado_ia = ""
        st.rerun()
