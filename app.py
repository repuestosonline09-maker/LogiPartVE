import streamlit as st
import requests
import json
import time

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="LogiPartVE Pro", layout="wide", page_icon="✈️")

# Carga de Secretos (Asegúrate de tenerlos en Streamlit Cloud o secrets.toml)
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASS_ADMIN = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("⚠️ Error: Configure 'Secrets' en Streamlit con GOOGLE_API_KEY y ADMIN_PASSWORD.")
    st.stop()

# ESTADOS DE SESIÓN (MEMORIA)
if 'resultado_ia' not in st.session_state: st.session_state.resultado_ia = ""
if 'count' not in st.session_state: st.session_state.count = 0
if 'tarifas' not in st.session_state: st.session_state.tarifas = {"mia_a": 9.0, "mia_m": 40.0, "mad": 20.0}

# 2. DISEÑO CSS PERSONALIZADO
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    .report-container { 
        padding: 20px; border-radius: 10px; background-color: #ffffff; 
        border: 2px solid #007bff; font-size: 15px; line-height: 1.5; color: #1e1e1e;
    }
    .manual-table { background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-top: 15px; border: 1px solid #dee2e6; }
    .stButton>button {width: 100%; height: 3em; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# 3. SIDEBAR (PANEL DE ADMINISTRACIÓN)
with st.sidebar:
    st.header("⚙️ Configuración")
    check_pass = st.text_input("Contraseña Admin", type="password")
    if check_pass == PASS_ADMIN:
        st.success("Acceso concedido")
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo ($/lb)", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo ($/ft³)", value=st.session_state.tarifas["mia_m"])
        st.session_state.tarifas["mad"] = st.number_input("MAD Aéreo ($/kg)", value=st.session_state.tarifas["mad"])
    else:
        st.info("Ingrese la clave para editar tarifas.")

# 4. ENCABEZADO
c1, c2 = st.columns([1, 6])
with c1: st.image("https://cdn-icons-png.flaticon.com/512/2208/2208233.png", width=70) 
with c2: st.title("LogiPartVE: Gestión Experta DDP")

# 5. FORMULARIO DE ENTRADA
with st.container():
    col1, col2, col3, col4, col5 = st.columns([2.5, 2, 2, 1.5, 1.5])
    with col1: v_in = st.text_input("Vehículo / Modelo", key=f"v_{st.session_state.count}")
    with col2: r_in = st.text_input("Nombre del Repuesto", key=f"r_{st.session_state.count}")
    with col3: n_in = st.text_input("Número de Parte", key=f"n_{st.session_state.count}")
    with col4: o_in = st.selectbox("Origen", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")
    with col5: t_in = st.selectbox("Tipo de Envío", ["Aéreo", "Marítimo"], key=f"t_{st.session_state.count}")

# 6. LÓGICA DE CONEXIÓN A GOOGLE GEMINI (OPTIMIZADO PARA PAGO)
if st.button("🚀 GENERAR ANÁLISIS Y COTIZACIÓN PROFESIONAL", type="primary"):
    if v_in and r_in and n_in:
        # URLs de alta capacidad (Nivel de Pago 1)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        url_back = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={API_KEY}"
        
        prompt = f"""
        ACTÚA COMO EXPERTO LOGÍSTICO DE LogiPartVE. 
        1. ANÁLISIS TÉCNICO: Identifica referencia {n_in} para {r_in} en vehículo {v_in}. Estima peso y dimensiones según estándares OEM.
        2. CÁLCULO DDP {o_in.upper()}: Usa peso mayor (Real vs Vol + 20% empaque). 
           Tarifas actuales: MIA Aé ${st.session_state.tarifas['mia_a']}, Mar ${st.session_state.tarifas['mia_m']} | MAD Aé ${st.session_state.tarifas['mad']}. Mínimo de guía: $25.
        3. STATUS RUTA: Alertas actualizadas a Diciembre 2025 sobre aduanas y clima para la ruta {o_in} -> Venezuela.
        """

        with st.spinner('Conectando con servidores de Google (Prioridad de Pago)...'):
            try:
                # Intento 1: Gemini 1.5 Flash (Rápido y eficiente)
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
                
                if res.status_code == 200:
                    st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
                else:
                    # Intento 2: Gemini 1.5 Pro (Respaldo de alta potencia)
                    res_back = requests.post(url_back, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
                    if res_back.status_code == 200:
                        st.session_state.resultado_ia = res_back.json()['candidates'][0]['content']['parts'][0]['text']
                    else:
                        # Diagnóstico en caso de error tras el pago
                        error_detail = res_back.json().get('error', {}).get('message', 'Error desconocido')
                        st.error(f"⚠️ Error de la API: {error_detail}")
                        st.info("Sugerencia: Si acabas de activar el pago, espera 5 minutos para que Google actualice tu estatus.")
            except Exception as e:
                st.error(f"❌ Error de conexión: {str(e)}")
    else:
        st.warning("Por favor, rellene todos los campos del vehículo, repuesto y número de parte.")

# 7. VISUALIZACIÓN DE RESULTADOS
if st.session_state.resultado_ia:
    st.markdown("### 📝 Análisis Logístico Generado")
    st.markdown(f'<div class="report-container">{st.session_state.resultado_ia}</div>', unsafe_allow_html=True)
    
    c_dw, c_cl = st.columns([5, 1])
    with c_dw: 
        st.download_button("📥 Descargar Cotización", st.session_state.resultado_ia, file_name=f"LogiPart_{n_in}.txt")
    with c_cl: 
        if st.button("🗑️ LIMPIAR"):
            st.session_state.count += 1
            st.session_state.resultado_ia = ""
            st.rerun()

# 8. CALCULADORA MANUAL (SEGURIDAD TOTAL)
st.markdown('<div class="manual-table">', unsafe_allow_html=True)
st.markdown("### 📊 Validación Manual de Costos")
mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
with mc1: l_cm = st.number_input("Largo (cm)", min_value=0.0)
with mc2: an_cm = st.number_input("Ancho (cm)", min_value=0.0)
with mc3: al_cm = st.number_input("Alto (cm)", min_value=0.0)
with mc4: p_kg = st.number_input("Peso (kg)", min_value=0.0)
with mc5: m_origen = st.selectbox("Origen", ["Miami", "Madrid"], key="man_or")
with mc6: m_tipo = st.selectbox("Tipo", ["Aéreo", "Marítimo"], key="man_ti")

if st.button("🧮 CALCULAR COSTO MANUAL"):
    p_vol_kg = (l_cm * an_cm * al_cm) / 5000
    p_final_kg = max(p_kg, p_vol_kg)
    if m_tipo == "Aéreo":
        factor = 2.20462 if m_origen == "Miami" else 1.0
        tarifa = st.session_state.tarifas["mia_a"] if m_origen == "Miami" else st.session_state.tarifas["mad"]
        costo = max((p_final_kg * factor) * tarifa, 25.0)
    else:
