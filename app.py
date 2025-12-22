import streamlit as st
import requests
import json

# 1. Configuración de página
st.set_page_config(page_title="LogiPartVE AI Pro", layout="wide", page_icon="🚛")

# Inicialización de llaves de estado para limpieza total
campos = ["vehiculo", "repuesto", "nro_parte", "origen"]
for campo in campos:
    if campo not in st.session_state:
        st.session_state[campo] = ""
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
st.title("🚛 LogiPartVE AI: Verificación y Cotización")

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        # Usamos st.session_state para permitir el borrado manual
        vehiculo_input = st.text_input("🚙 Vehículo (MARCA, MODELO, AÑO, CILINDRADA)", 
                                       placeholder="Ej: Toyota Hilux 2015 2.7L", 
                                       key="v_input")
        repuesto_input = st.text_input("🔧 Nombre del Repuesto", 
                                       placeholder="Ej: Bomba de Agua", 
                                       key="r_input")
    with c2:
        nro_parte_input = st.text_input("🏷️ NÚMERO DE PARTE (Exacto)", 
                                        placeholder="Ej: 16100-09442", 
                                        key="n_input")
        origen_input = st.selectbox("📍 ORIGEN DEL REPUESTO", 
                                     ["Miami", "Madrid"], 
                                     key="o_input")

# 5. Lógica de Petición con Filtro Estricto de Origen
c_btn1, c_btn2 = st.columns([4, 1])

with c_btn1:
    if st.button("🚀 VALIDAR Y COTIZAR", type="primary"):
        if not api_key: 
            st.error("⚠️ Falta API Key.")
        elif not vehiculo_input or not repuesto_input or not nro_parte_input:
            st.warning("⚠️ Los campos Vehículo, Repuesto y N° de Parte son OBLIGATORIOS.")
        else:
            try:
                list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                modelos_res = requests.get(list_url).json()
                modelos = [m['name'] for m in modelos_res.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
                url = f"https://generativelanguage.googleapis.com/v1beta/{modelos[0]}:generateContent?key={api_key}"

                # Instrucciones de bloqueo de origen
                if origen_input == "Miami":
                    instruccion_origen = f"Solo cotiza ruta MIAMI-VENEZUELA (Aéreo ${t_aereo_mia}/lb y Marítimo ${t_mar_mia}/ft³). PROHIBIDO mencionar Madrid."
                else:
                    instruccion_origen = f"Solo cotiza ruta MADRID-VENEZUELA (Aéreo ${t_mad}/kg). PROHIBIDO mencionar Miami o transporte marítimo."

                prompt = f"""
                ERES EL EXPERTO TÉCNICO DE LogiPartVE.
                
                VALIDACIÓN TÉCNICA: Verifica si el N° DE PARTE: {nro_parte_input} es para {repuesto_input} en {vehiculo_input}.
                Si hay error, responde: 'ERROR DE VALIDACIÓN TÉCNICA' y explica detalladamente por qué.
                
                SI ES CORRECTO, DA LA COTIZACIÓN ULTRA-RESUMIDA:
                - {instruccion_origen}
                - Peso y Medidas con empaque REFORZADO.
                - CUADRO DE EMBALAJE Y ALERTAS LOGÍSTICAS (retrasos, clima o aduanas para {origen_input}).
                
                Si no estás seguro de las medidas, responde 'NO LO SÉ'.
                """

                with st.spinner(f'🔍 Validando pieza y logística desde {origen_input}...'):
                    response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                    st.session_state.resultado_ia = response.json()['candidates'][0]['content']['parts'][0]['text']
            except: st.error("Error de conexión.")

with c_btn2:
    if st.button("🗑️ LIMPIAR"):
        # Borramos las llaves de los inputs
        st.session_state.v_input = ""
        st.session_state.r_input = ""
        st.session_state.n_input = ""
        st.session_state.resultado_ia = ""
        st.rerun()

# 6. Despliegue de Resultados
if st.session_state.resultado_ia:
    st.markdown("---")
    if "ERROR DE VALIDACIÓN TÉCNICA" in st.session_state.resultado_ia:
        st.error("❌ INCONSISTENCIA TÉCNICA DETECTADA")
    
    st.markdown(f'<div class="report-container">{st.session_state.resultado_ia}</div>', unsafe_allow_html=True)

    if "ERROR" in st.session_state.resultado_ia or "NO LO SÉ" in st.session_state.resultado_ia:
        with st.expander("📊 CALCULAR MANUALMENTE (Tarifas LogiPartVE)"):
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1: l = st.number_input("Largo (in)", value=0.0)
            with col_m2: an = st.number_input("Ancho (in)", value=0.0)
            with col_m3: al = st.number_input("Alto (in)", value=0.0)
            with col_m4: p = st.number_input("Peso", value=0.0)
            
            if st.button("Calcular"):
                if origen_input == "Miami":
                    a, m = p*t_aereo_mia, ((l*an*al)/1728)*t_mar_mia
                    st.success(f"MIA: Aéreo ${a:.2f} | Marítimo ${m:.2f}")
                else:
                    st.success(f"MAD: Aéreo ${p*t_mad:.2f}")

st.divider()
st.caption(f"LogiPartVE AI v3.0 | Tarifas: MIA Aéreo ${t_aereo_mia} - MAD ${t_mad} | Saliendo de {origen_input}")
