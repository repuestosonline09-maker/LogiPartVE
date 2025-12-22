import streamlit as st
import requests
import json

# 1. Configuración de página
st.set_page_config(page_title="LogiPartVE AI Pro", layout="wide", page_icon="🚛")

# Carga de Secretos Seguros
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASS_ADMIN = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("⚠️ Error: Configura los Secrets en Streamlit Cloud (GOOGLE_API_KEY y ADMIN_PASSWORD)")
    st.stop()

# Inicialización de estados
if 'resultado_ia' not in st.session_state:
    st.session_state.resultado_ia = ""
if 'count' not in st.session_state:
    st.session_state.count = 0
if 'tarifas' not in st.session_state:
    st.session_state.tarifas = {"mia_a": 9.0, "mia_m": 40.0, "mad": 20.0}

# 2. Estética
st.markdown("""
    <style>
    .report-container { padding: 20px; border-radius: 12px; border: 2px solid #007bff; white-space: pre-wrap; background-color: #f9f9f9; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar Administrativo
with st.sidebar:
    st.header("🔐 Panel LogiPartVE")
    check_pass = st.text_input("Acceso Admin", type="password")
    if check_pass == PASS_ADMIN:
        st.success("Modo Admin Activo")
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo ($/lb)", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo ($/ft³)", value=st.session_state.tarifas["mia_m"])
        st.session_state.tarifas["mad"] = st.number_input("MAD Aéreo ($/kg)", value=st.session_state.tarifas["mad"])
    else:
        st.info("Vendedores: No necesitan ingresar clave para cotizar.")

# 4. Interfaz del Vendedor
st.title("🚛 LogiPartVE AI: Cotizador Express")

c1, c2 = st.columns(2)
with c1:
    v_in = st.text_input("🚙 Vehículo (Marca, Modelo, Año, Cilindrada)", key=f"v_{st.session_state.count}")
    r_in = st.text_input("🔧 Repuesto", key=f"r_{st.session_state.count}")
with c2:
    n_in = st.text_input("🏷️ N° DE PARTE", key=f"n_{st.session_state.count}")
    o_in = st.selectbox("📍 ORIGEN", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")

# 5. Lógica de Petición
col_b1, col_b2 = st.columns([4,1])
with col_b1:
    if st.button("🚀 GENERAR COTIZACIÓN", type="primary"):
        if not v_in or not r_in or not n_in:
            st.warning("⚠️ Complete todos los campos.")
        else:
            try:
                # Detección de modelo
                url_m = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
                modelos = [m['name'] for m in requests.get(url_m).json().get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
                url = f"https://generativelanguage.googleapis.com/v1beta/{modelos[0]}:generateContent?key={API_KEY}"

                prompt = f"""
                ERES EL EXPERTO TÉCNICO DE LogiPartVE.
                1. VALIDA: N° {n_in} para {r_in} en {v_in}.
                2. LOGÍSTICA {o_in}: Sobredimensión 20%. Tarifas: MIA Aéreo ${st.session_state.tarifas['mia_a']}, Marítimo ${st.session_state.tarifas['mia_m']} | MAD Aéreo ${st.session_state.tarifas['mad']}.
                3. ALERTAS: Reporta noticias de retrasos, clima o aduanas actuales para {o_in} y Venezuela.
                Resumen corto, profesional y cuadro de embalaje.
                """
                
                with st.spinner('⏳ Validando y analizando logística...'):
                    res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                    st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
            except Exception as e:
                st.error(f"Error técnico: {e}")

with col_b2:
    if st.button("🗑️ LIMPIAR"):
        st.session_state.count += 1
        st.session_state.resultado_ia = ""
        st.rerun()

# 6. Despliegue
if st.session_state.resultado_ia:
    st.markdown("---")
    st.markdown(f'<div class="report-container">{st.session_state.resultado_ia}</div>', unsafe_allow_html=True)
