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

# 2. CSS Ultra-Compacto
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    .report-container { 
        padding: 15px; border-radius: 10px; background-color: #f8f9fa; 
        border: 1px solid #007bff; font-size: 14px; line-height: 1.3;
    }
    h1 {margin-bottom: 0px; font-size: 24px;}
    .stButton>button {height: 2.5em; margin-top: 10px;}
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar (Admin)
with st.sidebar:
    check_pass = st.text_input("Admin", type="password")
    if check_pass == PASS_ADMIN:
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo", value=st.session_state.tarifas["mia_m"])
        st.session_state.tarifas["mad"] = st.number_input("MAD Aéreo", value=st.session_state.tarifas["mad"])

# 4. Encabezado y Logo
c_logo1, c_logo2 = st.columns([1, 5])
with c_logo1:
    st.image("https://cdn-icons-png.flaticon.com/512/2208/2208233.png", width=70) # Reemplaza con tu logo
with c_logo2:
    st.title("LogiPartVE: Cotizador Puerta a Puerta")

# 5. Formulario Compacto
with st.container():
    c1, c2, c3, c4 = st.columns([2, 2, 2, 1.5])
    with c1: v_in = st.text_input("Vehículo", placeholder="Marca, Mod, Año, Cil", key=f"v_{st.session_state.count}")
    with c2: r_in = st.text_input("Repuesto", placeholder="Nombre", key=f"r_{st.session_state.count}")
    with c3: n_in = st.text_input("N° Parte", placeholder="OEM", key=f"n_{st.session_state.count}")
    with c4: o_in = st.selectbox("Origen", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")

# 6. Lógica
if st.button("🚀 COTIZAR AHORA", type="primary"):
    if v_in and r_in and n_in:
        try:
            url_res = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}").json()
            model_name = [m['name'] for m in url_res.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])][0]
            url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={API_KEY}"

            prompt = f"""
            ERES LOGIPARTVE. Resumen Ejecutivo Puerta a Puerta.
            VERIFICA: {n_in} para {r_in} ({v_in}).
            REGLA ESTRICTA: Solo calcula y muestra el origen {o_in.upper()}. No menciones el otro.
            
            CÁLCULO:
            1. Estima peso/medidas y suma +20% (Factor Seguridad Embalaje).
            2. TARIFAS: Miami (Aéreo ${st.session_state.tarifas['mia_a']}/lb, Mar ${st.session_state.tarifas['mia_m']}/ft³). Madrid (Aéreo ${st.session_state.tarifas['mad']}/kg).
            3. MINIMO: Si Aéreo < $25, advertir 'TARIFA MÍNIMA $25'.
            
            FORMATO DE SALIDA (Resumido):
            - Verificación Técnica.
            - Ficha: Peso (con +20%) | Medidas (con +20%).
            - Costo Total {o_in}: [Monto en $].
            - Recomendación Embalaje y Alertas Logísticas/Noticias actuales.
            """

            with st.spinner('Procesando...'):
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
        except: st.error("Error de conexión.")
    else: st.warning("Faltan datos.")

# 7. Resultados y Botón Limpiar
if st.session_state.resultado_ia:
    if "TARIFA MÍNIMA $25" in st.session_state.resultado_ia.upper():
        st.warning("⚠️ Mínimo de $25 aplicable.")
    
    st.markdown(f'<div class="report-container">{st.session_state.resultado_ia}</div>', unsafe_allow_html=True)
    
    c_dw, c_cl = st.columns([4, 1])
    with c_dw: st.download_button("📥 Descargar", st.session_state.resultado_ia, file_name="cotizacion.txt")
    with c_cl: 
        if st.button("🗑️ LIMPIAR"):
            st.session_state.count += 1
            st.session_state.resultado_ia = ""
            st.rerun()

st.caption(f"v4.5 | Puerta a Puerta | Tarifas: MIA A:{st.session_state.tarifas['mia_a']} M:{st.session_state.tarifas['mia_m']} | MAD:{st.session_state.tarifas['mad']}")
