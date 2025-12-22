import streamlit as st
import requests
import json

# 1. Configuración de página
st.set_page_config(page_title="LogiPartVE AI Pro", layout="wide", page_icon="🚛")

# Inicialización de llaves de estado
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
    .hazmat-warning { color: #856404; background-color: #fff3cd; padding: 10px; border-radius: 5px; margin-top: 10px; border: 1px solid #ffeeba; }
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar: Panel Administrativo
with st.sidebar:
    st.header("🔐 Admin LogiPartVE")
    admin_pass = st.text_input("Password", type="password")
    api_key, t_aereo_mia, t_mar_mia, t_mad = "", 9.0, 40.0, 20.0
    if admin_pass == "admin123":
        api_key = st.text_input("Google API Key", type="password")
        t_aereo_mia = st.number_input("MIA Aéreo ($/lb)", value=9.0)
        t_mar_mia = st.number_input("MIA Marítimo ($/ft³)", value=40.0)
        t_mad = st.number_input("MAD Aéreo ($/kg)", value=20.0)

# 4. Interfaz de Usuario
st.title("🚛 LogiPartVE AI: Auditoría Técnica y Logística")

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        v_in = st.text_input("🚙 Vehículo (Marca, Modelo, Año, Cilindrada)", placeholder="Ej: Ford Explorer 2017 3.5L EcoBoost", key="v_field")
        r_in = st.text_input("🔧 Nombre del Repuesto", placeholder="Ej: Airbag de Volante o Amortiguador", key="r_field")
    with c2:
        n_in = st.text_input("🏷️ NÚMERO DE PARTE", placeholder="Ej: GB5Z-78043B13-B", key="n_field")
        o_in = st.selectbox("📍 ORIGEN DEL REPUESTO", ["Miami", "Madrid"], key="o_field")

# 5. Lógica con Normativas y Sobredimensión
c_btn1, c_btn2 = st.columns([4, 1])

with c_btn1:
    if st.button("🚀 VALIDAR Y COTIZAR", type="primary"):
        if not api_key: st.error("⚠️ Configure la API Key.")
        elif not v_in or not r_in or not n_in: st.warning("⚠️ Todos los campos son obligatorios.")
        else:
            try:
                list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                modelos = [m['name'] for m in requests.get(list_url).json().get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
                url = f"https://generativelanguage.googleapis.com/v1beta/{modelos[0]}:generateContent?key={api_key}"

                prompt = f"""
                ERES EL EXPERTO TÉCNICO DE LogiPartVE.
                
                VALIDACIÓN TÉCNICA: Verifica compatibilidad de N° {n_in} para {r_in} en {v_in}.
                Si hay error, responde: 'ERROR DE VALIDACIÓN TÉCNICA' y explica.

                SI ES CORRECTO, COTIZA DESDE {o_in} BAJO ESTAS REGLAS:
                1. ORIGEN EXCLUSIVO: Solo usa tarifas de {o_in}. (MIA: $9/lb, $40/ft³ | MAD: $20/kg).
                2. FACTOR DE SEGURIDAD: Calcula dimensiones con un margen extra del 15-20% para empaques reforzados del proveedor.
                3. NORMATIVAS Y HAZMAT: Identifica si el producto es carga peligrosa (aceites, gases, airbags, baterías, imanes). 
                   Si aplica, explica por qué el costo podría aumentar (impuestos Hazmat o manejo especial).
                
                ESTRUCTURA:
                - Ficha Técnica y Verificación.
                - Logística (Peso/Medidas con sobremargen).
                - Costos (Comparativa Aéreo/Marítimo si es Miami).
                - CUADRO DE RECOMENDACIONES, NORMATIVAS Y ALERTAS LOGÍSTICAS.
                """

                with st.spinner('🔍 Auditando normativas y dimensiones...'):
                    response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                    st.session_state.resultado_ia = response.json()['candidates'][0]['content']['parts'][0]['text']
            except: st.error("Error de conexión.")

with c_btn2:
    if st.button("🗑️ LIMPIAR"):
        # Limpieza manual de cada campo
        st.session_state.v_field = ""
        st.session_state.r_field = ""
        st.session_state.n_field = ""
        st.session_state.resultado_ia = ""
        st.rerun()

# 6. Despliegue
if st.session_state.resultado_ia:
    st.markdown("---")
    st.markdown(f'<div class="report-container">{st.session_state.resultado_ia}</div>', unsafe_allow_html=True)

    # Identificación visual de advertencias Hazmat en la respuesta
    if any(word in st.session_state.resultado_ia.upper() for word in ["HAZMAT", "PELIGROSA", "RESTRICTO", "GAS", "INFLAMABLE"]):
        st.warning("⚠️ Esta mercancía puede estar sujeta a recargos por Normativas Internacionales de Seguridad.")

st.divider()
st.caption(f"LogiPartVE AI v3.5 | Factor de Seguridad de Empaque Activo | Auditoría Hazmat")
