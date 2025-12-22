import streamlit as st
import requests
import json

# 1. Configuración de página
st.set_page_config(page_title="LogiPartVE Pro", layout="wide", page_icon="✈️")

# Carga de Secretos (Protección de ADN)
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASS_ADMIN = st.secrets["ADMIN_PASSWORD"]
except:
    st.error("⚠️ Error: Configure las credenciales en 'Secrets' de Streamlit.")
    st.stop()

# Estados de sesión
if 'resultado_ia' not in st.session_state: st.session_state.resultado_ia = ""
if 'count' not in st.session_state: st.session_state.count = 0
if 'tarifas' not in st.session_state: st.session_state.tarifas = {"mia_a": 9.0, "mia_m": 40.0, "mad": 20.0}

# 2. CSS Ultra-Compacto
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    .report-container { 
        padding: 15px; border-radius: 10px; background-color: #ffffff; 
        border: 2px solid #007bff; font-size: 14px; line-height: 1.3;
    }
    .manual-table { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-top: 10px; border: 1px solid #d1d5db; }
    .stButton>button {height: 2.8em;}
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar (Admin)
with st.sidebar:
    st.header("⚙️ Admin")
    check_pass = st.text_input("Contraseña", type="password")
    if check_pass == PASS_ADMIN:
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo ($/lb)", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo ($/ft³)", value=st.session_state.tarifas["mia_m"])
        st.session_state.tarifas["mad"] = st.number_input("MAD Aéreo ($/kg)", value=st.session_state.tarifas["mad"])

# 4. Encabezado
c_logo1, c_logo2 = st.columns([1, 5])
with c_logo1:
    st.image("https://cdn-icons-png.flaticon.com/512/2208/2208233.png", width=60) 
with c_logo2:
    st.title("LogiPartVE: Cotizador Experto v5.4")

# 5. Formulario Principal
with st.container():
    c1, c2, c3, c4, c5 = st.columns([2.5, 2, 2, 1.2, 1.2])
    with c1: v_in = st.text_input("Vehículo", key=f"v_{st.session_state.count}")
    with c2: r_in = st.text_input("Repuesto", key=f"r_{st.session_state.count}")
    with c3: n_in = st.text_input("N° Parte", key=f"n_{st.session_state.count}")
    with c4: o_in = st.selectbox("Origen", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")
    with c5: t_in = st.selectbox("Envío", ["Aéreo", "Marítimo"], key=f"t_{st.session_state.count}")

# 6. Lógica de IA (Modelo Fijo para evitar Errores de Procesamiento)
if st.button("🚀 GENERAR ANÁLISIS Y COTIZACIÓN", type="primary"):
    if v_in and r_in and n_in:
        try:
            # Apuntamos directamente al modelo estable
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

            prompt = f"""
            ACTÚA COMO EXPERTO SENIOR EN RECAMBIOS Y LOGÍSTICA DDP VENEZUELA. 
            
            1. ANÁLISIS TÉCNICO (RESUMIDO): Identifica {n_in} para {r_in} ({v_in}). 
               - Menciona sustitutos actuales. USA TU CONOCIMIENTO de pesos y medidas originales.
            
            2. COTIZACIÓN (RESUMIDA):
               - Muestra Peso Físico, Dimensiones y Peso a Facturar (Mayor entre Físico y Volumétrico + 20% seguridad).
               - Tarifas: MIA Aé ${st.session_state.tarifas['mia_a']}, Mar ${st.session_state.tarifas['mia_m']} | MAD Aé ${st.session_state.tarifas['mad']}.
               - REGLA MÍNIMO: Si Total Aéreo < $25, advierte 'TARIFA MÍNIMA $25'.

            3. MONITOREO DE NOTICIAS Y ALERTAS (EXTENSO Y DETALLADO):
               - Análisis profundo de noticias actuales al 22 de diciembre 2025 que afecten la ruta {o_in} a Venezuela (Clima, Aduanas, Puertos, retrasos regionales).
            """

            with st.spinner('Procesando datos técnicos y noticias...'):
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
                # Verificación de respuesta
                if res.status_code == 200:
                    st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
                else:
                    st.error(f"Error de API ({res.status_code}): {res.text}")
        except Exception as e:
            st.error(f"Error técnico de conexión: {str(e)}")
    else:
        st.warning("Por favor, complete todos los campos.")

# 7. Resultados
if st.session_state.resultado_ia:
    st.markdown(f'<div class="report-container">{st.session_state.resultado_ia}</div>', unsafe_allow_html=True)
    c_dw, c_cl = st.columns([5, 1])
    with c_dw: st.download_button("📥 Descargar", st.session_state.resultado_ia, file_name="cotizacion.txt")
    with c_cl: 
        if st.button("🗑️ LIMPIAR"):
            st.session_state.count += 1
            st.session_state.resultado_ia = ""
            st.rerun()

# 8. TABLA MANUAL
st.markdown('<div class="manual-table">', unsafe_allow_html=True)
st.markdown("### 📊 Validación Manual Directa")
mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
with mc1: l_cm = st.number_input("Largo (cm)", min_value=0.0, key="ml")
with mc2: an_cm = st.number_input("Ancho (cm)", min_value=0.0, key="man")
with mc3: al_cm = st.number_input("Alto (cm)", min_value=0.0, key="mal")
with mc4: p_kg = st.number_input("Peso (kg)", min_value=0.0, key="mp")
with mc5: m_origen = st.selectbox("Origen", ["Miami", "Madrid"], key="mo")
with mc6: m_tipo = st.selectbox("Tipo", ["Aéreo", "Marítimo"], key="mt")

if st.button("🧮 CALCULAR"):
    p_vol_kg = (l_cm * an_cm * al_cm) / 5000
    p_final_kg = max(p_kg, p_vol_kg)
    if m_tipo == "Aéreo":
        factor = 2.20462 if m_origen == "Miami" else 1.0
        tarifa = st.session_state.tarifas["mia_a"] if m_origen == "Miami" else st.session_state.tarifas["mad"]
        costo = max((p_final_kg * factor) * tarifa, 25.0)
    else:
        ft3 = (l_cm * an_cm * al_cm) / 28316.8
        costo = ft3 * st.session_state.tarifas["mia_m"]
    st.success(f"**Costo Estimado: ${costo:.2f} USD**")
st.markdown('</div>', unsafe_allow_html=True)
