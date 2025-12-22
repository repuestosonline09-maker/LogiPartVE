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
    .error-box { padding: 15px; background-color: #ffebee; border-left: 5px solid #f44336; margin-bottom: 10px; }
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

# 4. Interfaz de Usuario (Entrada de Datos Críticos)
st.title("🚛 LogiPartVE AI: Verificación Técnica y Logística")

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        vehiculo = st.text_input("🚙 Vehículo (MARCA, MODELO, AÑO, CILINDRADA)", placeholder="Ej: Toyota Hilux 2015 2.7L")
        repuesto = st.text_input("🔧 Nombre del Repuesto", placeholder="Ej: Bomba de Agua")
    with c2:
        nro_parte = st.text_input("🏷️ NÚMERO DE PARTE (Exacto)", placeholder="Ej: 16100-09442")
        origen = st.selectbox("📍 Origen del Repuesto", ["Miami", "Madrid"])

# 5. Lógica de Petición con Validación Técnica
c_btn1, c_btn2 = st.columns([4, 1])

with c_btn1:
    if st.button("🚀 VALIDAR Y COTIZAR", type="primary"):
        if not api_key: st.error("⚠️ Falta API Key.")
        elif not vehiculo or not repuesto or not nro_parte:
            st.warning("⚠️ Los campos Vehículo, Repuesto y N° de Parte son OBLIGATORIOS para la verificación.")
        else:
            try:
                list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                modelos = [m['name'] for m in requests.get(list_url).json().get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
                url = f"https://generativelanguage.googleapis.com/v1beta/{modelos[0]}:generateContent?key={api_key}"

                prompt = f"""
                ERES EL EXPERTO TÉCNICO Y LOGÍSTICO DE LogiPartVE.
                
                TU PRIMERA MISIÓN: Verificar si el N° DE PARTE: {nro_parte} corresponde al REPUESTO: {repuesto} para el VEHÍCULO: {vehiculo}.
                
                SI HAY UN ERROR DE COMPATIBILIDAD:
                - Detén la cotización.
                - Explica al vendedor por qué el número no coincide (ej: es para otro año, otro motor o es un número sustituido).
                - Responde con el texto: 'ERROR DE VALIDACIÓN TÉCNICA'.
                
                SI TODO ES CORRECTO:
                1. Da una ficha técnica ultra-resumida.
                2. Estima Peso y Medidas con EMPAQUE REFORZADO.
                3. COSTOS: 
                   - Miami: Aéreo (${t_aereo_mia}/lb) y Marítimo (${t_mar_mia}/ft³).
                   - Madrid: Solo Aéreo (${t_mad}/kg).
                4. CUADRO DE EMBALAJE Y ALERTAS GLOBALES:
                   - Sugerencia de protección.
                   - Alertas de retrasos actuales en {origen} o Venezuela (clima, aduanas, huelgas).
                """

                with st.spinner('🔍 Verificando compatibilidad de pieza...'):
                    response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                    st.session_state.resultado_ia = response.json()['candidates'][0]['content']['parts'][0]['text']
            except: st.error("Error de conexión.")

with c_btn2:
    if st.button("🗑️ LIMPIAR"):
        st.session_state.resultado_ia = ""
        st.rerun()

# 6. Despliegue y Calculadora Manual de Emergencia
if st.session_state.resultado_ia:
    st.markdown("---")
    
    if "ERROR DE VALIDACIÓN TÉCNICA" in st.session_state.resultado_ia:
        st.error("❌ INCONSISTENCIA DETECTADA")
        st.markdown(f'<div class="error-box">{st.session_state.resultado_ia}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="report-container">{st.session_state.resultado_ia}</div>', unsafe_allow_html=True)

    # Si hay error o falta de datos, se ofrece la tabla manual
    if "ERROR" in st.session_state.resultado_ia or "NO LO SÉ" in st.session_state.resultado_ia:
        st.info("💡 Puede proceder con una cotización basada en medidas manuales si posee el paquete físico.")
        with st.expander("📊 TABLA DE COTIZACIÓN MANUAL"):
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1: l = st.number_input("Largo (in)")
            with col_m2: an = st.number_input("Ancho (in)")
            with col_m3: al = st.number_input("Alto (in)")
            with col_m4: p = st.number_input("Peso")
            
            if st.button("Calcular Manualmente"):
                if origen == "Miami":
                    aereo = p * t_aereo_mia
                    marit = ((l*an*al)/1728) * t_mar_mia
                    st.success(f"MIA: Aéreo ${aereo:.2f} | Marítimo ${marit:.2f}")
                else:
                    st.success(f"MAD: Aéreo ${p * t_mad:.2f}")

st.divider()
st.caption("LogiPartVE AI - Sistema de Auditoría Técnica y Logística de Autopartes.")
