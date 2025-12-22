import streamlit as st
import requests
import json

# 1. Configuración de página
st.set_page_config(page_title="LogiPartVE AI Pro", layout="wide", page_icon="🚛")

# Inicialización de estados necesarios
if 'resultado_ia' not in st.session_state:
    st.session_state.resultado_ia = ""
# Usamos un contador para forzar el reinicio de los widgets
if 'count' not in st.session_state:
    st.session_state.count = 0

# 2. Estética LogiPartVE
st.markdown("""
    <style>
    .report-container { 
        padding: 20px; border-radius: 12px; background-color: #ffffff; 
        border: 2px solid #007bff; color: #1a1a1a; white-space: pre-wrap;
    }
    .stButton>button { border-radius: 8px; height: 3.5em; font-weight: bold; }
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
st.title("🚛 LogiPartVE AI: Auditoría Técnica y Logística")

# Usamos la técnica de "key dinámica" basada en st.session_state.count para limpiar
with st.container():
    c1, c2 = st.columns(2)
    with c1:
        v_in = st.text_input("🚙 Vehículo (Marca, Modelo, Año, Cilindrada)", 
                             placeholder="Ej: Ford Explorer 2017 3.5L EcoBoost", 
                             key=f"v_field_{st.session_state.count}")
        r_in = st.text_input("🔧 Nombre del Repuesto", 
                             placeholder="Ej: Airbag o Amortiguadores", 
                             key=f"r_field_{st.session_state.count}")
    with c2:
        n_in = st.text_input("🏷️ NÚMERO DE PARTE", 
                             placeholder="Ej: GB5Z-78043B13-B", 
                             key=f"n_field_{st.session_state.count}")
        o_in = st.selectbox("📍 ORIGEN DEL REPUESTO", 
                            ["Miami", "Madrid"], 
                            key=f"o_field_{st.session_state.count}")

# 5. Lógica de Petición
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
                2. LOGÍSTICA DE {o_in}: Aplica factor de seguridad (sobremedida del 15-20%). MIA: $9/lb, $40/ft³ | MAD: $20/kg.
                3. ALERTAS DE NOTICIAS REAL-TIME: Analiza noticias mundiales y regionales (huelgas, clima, aduanas) que afecten envíos a Venezuela HOY.
                4. RECOMENDACIÓN DE EMBALAJE: Según fragilidad.
                Respuesta corta y profesional. Si no sabes peso/medida, di 'NO LO SÉ'.
                """

                with st.spinner('🔍 Analizando pieza y situación global...'):
                    response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                    st.session_state.resultado_ia = response.json()['candidates'][0]['content']['parts'][0]['text']
            except: st.error("Error al conectar con la inteligencia logística.")

with c_btn2:
    if st.button("🗑️ LIMPIAR"):
        # Aumentamos el contador: esto hace que Streamlit crea que son widgets nuevos y los limpie
        st.session_state.count += 1
        st.session_state.resultado_ia = ""
        st.rerun()

with c_btn3:
    if st.session_state.resultado_ia:
        st.download_button("📥 EXPORTAR", st.session_state.resultado_ia, file_name="cotizacion_LogiPartVE.txt")

# 6. Despliegue de Resultados
if st.session_state.resultado_ia:
    st.markdown("---")
    st.markdown(f'<div class="report-container">{st.session_state.resultado_ia}</div>', unsafe_allow_html=True)
    
    if any(word in st.session_state.resultado_ia.upper() for word in ["NO SE PUEDE", "PROHIBIDO", "RETRASO", "HUELGA"]):
        st.warning("🚨 Revisar sección de ALERTAS LOGÍSTICAS antes de confirmar al cliente.")

st.divider()
st.caption("LogiPartVE AI v4.1 | Auditoría de Seguridad y Logística")
