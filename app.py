import streamlit as st
import requests
import json

# 1. Configuración de página
st.set_page_config(page_title="LogiPartVE AI Pro", layout="wide", page_icon="✈️")

# Carga de Secretos Seguros
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASS_ADMIN = st.secrets["ADMIN_PASSWORD"]
except Exception:
    st.error("⚠️ Error: Configure GOOGLE_API_KEY y ADMIN_PASSWORD en los Secrets de Streamlit.")
    st.stop()

# Inicialización de estados
if 'resultado_ia' not in st.session_state:
    st.session_state.resultado_ia = ""
if 'count' not in st.session_state:
    st.session_state.count = 0
if 'tarifas' not in st.session_state:
    st.session_state.tarifas = {"mia_a": 9.0, "mia_m": 40.0, "mad": 20.0}

# 2. Estética Personalizada
st.markdown("""
    <style>
    .report-container { 
        padding: 25px; border-radius: 12px; background-color: #ffffff; 
        border: 2px solid #007bff; color: #1a1a1a; white-space: pre-wrap;
        font-family: Arial, sans-serif;
    }
    .stButton>button { border-radius: 8px; height: 3.5em; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar Administrativo
with st.sidebar:
    st.header("🔐 Panel Master")
    check_pass = st.text_input("Contraseña Admin", type="password")
    if check_pass == PASS_ADMIN:
        st.success("Modo Admin Activo")
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo ($/lb)", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo ($/ft³)", value=st.session_state.tarifas["mia_m"])
        st.session_state.tarifas["mad"] = st.number_input("MAD Aéreo ($/kg)", value=st.session_state.tarifas["mad"])
    else:
        st.info("Vendedores: No requieren clave para cotizar.")

# --- SECCIÓN DEL LOGO Y TÍTULO ---
col_l1, col_l2 = st.columns([1, 4])
with col_l1:
    # Espacio para tu enlace de logo
    st.image("https://cdn-icons-png.flaticon.com/512/2208/2208233.png", width=120) 
with col_l2:
    st.title("LogiPartVE AI: Cotizador Express")

# 4. Interfaz del Vendedor
with st.container():
    c1, c2 = st.columns(2)
    with c1:
        v_in = st.text_input("🚙 Vehículo (Marca, Modelo, Año, Cilindrada)", key=f"v_{st.session_state.count}", placeholder="Ej: Ford Explorer 2017 3.5L")
        r_in = st.text_input("🔧 Repuesto", key=f"r_{st.session_state.count}", placeholder="Ej: Amortiguadores")
    with c2:
        n_in = st.text_input("🏷️ N° DE PARTE", key=f"n_{st.session_state.count}", placeholder="Ej: GB5Z-18125-A")
        o_in = st.selectbox("📍 ORIGEN", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")

# 5. Lógica de Petición
if st.button("🚀 GENERAR COTIZACIÓN DE ENVÍO", type="primary"):
    if not v_in or not r_in or not n_in:
        st.warning("⚠️ Complete todos los datos del repuesto.")
    else:
        try:
            # Obtención de modelo compatible
            url_list = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
            response_models = requests.get(url_list).json()
            modelos = [m['name'] for m in response_models.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
            
            if not modelos:
                st.error("No se encontraron modelos disponibles.")
            else:
                url = f"https://generativelanguage.googleapis.com/v1beta/{modelos[0]}:generateContent?key={API_KEY}"

                # PROMPT REFORZADO PARA CÁLCULOS
                prompt = f"""
                ERES EL EXPERTO TÉCNICO Y LOGÍSTICO DE LogiPartVE.
                
                PRODUCTO: {r_in} para {v_in}, N° Parte: {n_in}.
                ORIGEN: {o_in}.
                
                INSTRUCCIONES DE CÁLCULO:
                1. VALIDA compatibilidad. Si hay error, detén y explica.
                2. SOBREDIMENSIÓN: Estima peso y medidas originales, pero AUMENTA un 20% el volumen para el cálculo final.
                3. MATEMÁTICA OBLIGATORIA (Muestra el procedimiento):
                   - Si es MIAMI: 
                     * Aéreo: Peso(lb) x ${st.session_state.tarifas['mia_a']}.
                     * Marítimo: (Largo x Ancho x Alto / 1728) x ${st.session_state.tarifas['mia_m']}.
                   - Si es MADRID:
                     * Aéreo: Peso(kg) x ${st.session_state.tarifas['mad']}.
                
                4. ALERTAS: Noticias actuales (clima, huelgas, aduanas Venezuela) y normativas Hazmat.
                
                Respuesta ultra-resumida con cuadros de costos finales en $.
                """

                with st.spinner('⏳ Validando y Calculando...'):
                    res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                    st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            st.error(f"Error en la conexión con la IA: {str(e)}")

# Botón Limpiar
if st.button("🗑️ LIMPIAR"):
    st.session_state.count += 1
    st.session_state.resultado_ia = ""
    st.rerun()

# 6. Despliegue de Resultados
if st.session_state.resultado_ia:
    st.markdown("---")
    st.markdown(f'<div class="report-container">{st.session_state.resultado_ia}</div>', unsafe_allow_html=True)
    st.download_button("📥 Exportar Presupuesto", st.session_state.resultado_ia, file_name="cotizacion_logipartve.txt")
