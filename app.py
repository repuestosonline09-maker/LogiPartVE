import streamlit as st
import requests
import json

# 1. Configuración de página
st.set_page_config(page_title="LogiPartVE AI Pro", layout="wide", page_icon="🚛")

if 'resultado_ia' not in st.session_state:
    st.session_state.resultado_ia = ""

# 2. Estética LogiPartVE
st.markdown("""
    <style>
    .report-container { 
        padding: 20px; border-radius: 12px; background-color: #ffffff; 
        border: 2px solid #007bff; color: #1a1a1a; white-space: pre-wrap;
    }
    .stButton>button { border-radius: 8px; height: 3.5em; font-weight: bold; }
    .hazmat-warning { color: #856404; background-color: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0; border: 1px solid #ffeeba; }
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar: Panel Administrativo
with st.sidebar:
    st.header("🔐 Admin LogiPartVE")
    admin_pass = st.text_input("Contraseña", type="password")
    api_key, t_aereo_mia, t_mar_mia, t_mad = "", 9.0, 40.0, 20.0
    if admin_pass == "admin123":
        api_key = st.text_input("Google API Key", type="password")
        t_aereo_mia = st.number_input("MIA Aéreo ($/lb)", value=9.0)
        t_mar_mia = st.number_input("MIA Marítimo ($/ft³)", value=40.0)
        t_mad = st.number_input("MAD Aéreo ($/kg)", value=20.0)

# 4. Interfaz de Usuario
st.title("🚛 LogiPartVE AI: Auditoría Técnica y Logística Real-Time")

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        v_in = st.text_input("🚙 Vehículo (Marca, Modelo, Año, Cilindrada)", placeholder="Ej: Ford Explorer 2017 3.5L EcoBoost", key="v_field")
        r_in = st.text_input("🔧 Nombre del Repuesto", placeholder="Ej: Airbag o Amortiguadores", key="r_field")
    with c2:
        n_in = st.text_input("🏷️ NÚMERO DE PARTE", placeholder="Ej: GB5Z-78043B13-B", key="n_field")
        o_in = st.selectbox("📍 ORIGEN DEL REPUESTO", ["Miami", "Madrid"], key="o_field")

# 5. Lógica de Petición con Noticias y Normativas
c_btn1, c_btn2, c_btn3 = st.columns([3, 1, 1])

with c_btn1:
    if st.button("🚀 VALIDAR Y COTIZAR", type="primary"):
        if not api_key: st.error("⚠️ Configure la API Key en el Panel Lateral.")
        elif not v_in or not r_in or not n_in: st.warning("⚠️ Todos los campos son obligatorios.")
        else:
            try:
                list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                modelos = [m['name'] for m in requests.get(list_url).json().get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
                url = f"https://generativelanguage.googleapis.com/v1beta/{modelos[0]}:generateContent?key={api_key}"

                prompt = f"""
                ERES EL EXPERTO TÉCNICO Y LOGÍSTICO DE LogiPartVE.
                
                1. VALIDACIÓN TÉCNICA: Verifica compatibilidad de N° {n_in} para {r_in} en {v_in}.
                   Si hay error, responde: 'ERROR DE VALIDACIÓN TÉCNICA' y explica detalladamente.

                2. LOGÍSTICA DE {o_in}: 
                   - Aplica factor de seguridad (sobremedida del 15-20% para cajas de protección).
                   - MIA: $9/lb aéreo, $40/ft³ marítimo. | MAD: $20/kg aéreo.

                3. ALERTAS DE NOTICIAS Y LOGÍSTICA REAL-TIME: 
                   - Analiza noticias globales y regionales actuales (clima, huelgas, huelgas portuarias, conflictos, saturación aduanera en Venezuela).
                   - Reporta CUALQUIER situación que pueda retrasar la entrega o impedir el envío de {r_in} desde {o_in}.
                   - Si el producto es HAZMAT o prohibido por leyes internacionales, explícalo.

                ESTRUCTURA DE RESPUESTA:
                - RESULTADO DE VERIFICACIÓN TÉCNICA.
                - FICHA LOGÍSTICA (Peso/Medidas reforzadas).
                - COSTOS ESTIMADOS (Comparativa si es Miami).
                - CUADRO DE EMBALAJE RECOMENDADO.
                - ⚠️ ALERTAS LOGÍSTICAS Y NOTICIAS ACTUALES: (Informa sobre la viabilidad del envío hoy).
                """

                with st.spinner('🔍 Analizando compatibilidad y situación logística global...'):
                    response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                    st.session_state.resultado_ia = response.json()['candidates'][0]['content']['parts'][0]['text']
            except: st.error("Error al conectar con la inteligencia logística.")

with c_btn2:
    if st.button("🗑️ LIMPIAR"):
        st.session_state.v_field = ""
        st.session_state.r_field = ""
        st.session_state.n_field = ""
        st.session_state.resultado_ia = ""
        st.rerun()

with c_btn3:
    if st.session_state.resultado_ia:
        st.download_button("📥 EXPORTAR", st.session_state.resultado_ia, file_name="presupuesto_logipartve.txt")

# 6. Despliegue de Resultados
if st.session_state.resultado_ia:
    st.markdown("---")
    st.markdown(f'<div class="report-container">{st.session_state.resultado_ia}</div>', unsafe_allow_html=True)

    if any(word in st.session_state.resultado_ia.upper() for word in ["NO SE PUEDE", "PROHIBIDO", "RETRASO CRÍTICO", "HUELGA", "BLOQUEO"]):
        st.error("🚨 ALERTA CRÍTICA: Se han detectado factores que comprometen la viabilidad o el tiempo de entrega.")

st.divider()
st.caption(f"LogiPartVE AI v4.0 | Monitoreo Global en Tiempo Real | Tarifas: MIA Aéreo ${t_aereo_mia} - MAD ${t_mad}")
