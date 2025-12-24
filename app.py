import streamlit as st
import requests
import json
import os
import base64

# 1. CONFIGURACIÓN DE PÁGINA PROFESIONAL
st.set_page_config(page_title="LogiPartVE Pro", layout="wide", page_icon="✈️")

# Nombre del archivo de imagen en tu repositorio
logo_filename = "logo.png"

# --- LÓGICA DE DISEÑO ADAPTABLE (CSS) ---
st.markdown(
    """
    <style>
    @media (max-width: 640px) {
        .main-logo-container { width: 120px !important; margin: 0 auto; }
    }
    @media (min-width: 641px) {
        .main-logo-container { width: 180px !important; margin: 0 auto; }
    }
    .stImage > img {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 2. CARGA DE SECRETOS Y SEGURIDAD
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASS_ADMIN = st.secrets["ADMIN_PASSWORD"]
except Exception:
    st.error("⚠️ Error crítico: Configure 'Secrets' en Streamlit Cloud.")
    st.stop()

# ESTADOS DE SESIÓN PARA PERSISTENCIA
if 'resultado_ia' not in st.session_state: st.session_state.resultado_ia = ""
if 'count' not in st.session_state: st.session_state.count = 0
if 'tarifas' not in st.session_state: 
    st.session_state.tarifas = {"mia_a": 9.0, "mia_m": 40.0, "mad": 20.0}

# --- PANEL CENTRAL: LOGOTIPO INTELIGENTE ---
c_left, c_logo, c_right = st.columns([1.5, 1, 1.5])
with c_logo:
    if os.path.exists(logo_filename):
        with open(logo_filename, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        st.markdown(f'<div class="main-logo-container"><img src="data:image/png;base64,{data}" style="width:100%"></div>', unsafe_allow_html=True)
    else:
        st.info("💡 Cargando Identidad...")

# --- BARRA LATERAL (ADMIN) ---
with st.sidebar:
    sc1, sc2, sc3 = st.columns([1, 2, 1])
    with sc2:
        if os.path.exists(logo_filename):
            st.image(logo_filename, use_container_width=True)
    
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; font-size: 18px;'>Tarifas Admin</h2>", unsafe_allow_html=True)
    check_pass = st.text_input("Contraseña", type="password")
    
    if check_pass == PASS_ADMIN:
        st.success("Acceso Autorizado")
        st.session_state.tarifas["mia_a"] = st.number_input("MIA Aéreo ($/lb)", value=st.session_state.tarifas["mia_a"])
        st.session_state.tarifas["mia_m"] = st.number_input("MIA Marítimo ($/ft³)", value=st.session_state.tarifas["mia_m"])
        st.session_state.tarifas["mad"] = st.number_input("MAD Aéreo ($/kg)", value=st.session_state.tarifas["mad"])

# 3. TÍTULO PRINCIPAL
st.markdown("<h1 style='text-align: center; color: #1E3A8A; font-size: 32px; margin-top: -10px;'>Inteligencia Automotriz DDP</h1>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# 4. FORMULARIO DE CONSULTA
col1, col2, col3, col4, col5 = st.columns([2.5, 2, 2, 1.5, 1.5])
with col1: v_in = st.text_input("Vehículo / Modelo", key=f"v_{st.session_state.count}")
with col2: r_in = st.text_input("Nombre del Repuesto", key=f"r_{st.session_state.count}")
with col3: n_in = st.text_input("Número de Parte", key=f"n_{st.session_state.count}")
with col4: o_in = st.selectbox("Origen", ["Miami", "Madrid"], key=f"o_{st.session_state.count}")
with col5: t_in = st.selectbox("Envío", ["Aéreo", "Marítimo"], key=f"t_{st.session_state.count}")

# 5. CEREBRO TÉCNICO: EL ASESOR EXPERTO Y CONSULTOR OEM
if st.button("🚀 GENERAR ANÁLISIS TÉCNICO", type="primary", use_container_width=True):
    if v_in and r_in and n_in:
        prompt_tecnico = f"""
        ERES EL PERITO TÉCNICO SENIOR DE LogiPartVE. 
        EXPERTO EN CATÁLOGOS OEM (MOPAR, MOTORCRAFT, AC DELCO, TOYOTA, ETC.) Y MARCAS GENÉRICAS DE ALTO NIVEL.

        DATOS A EVALUAR:
        - Vehículo: {v_in}
        - Repuesto: {r_in}
        - N° de Parte dado por cliente: {n_in}

        TAREA 1: AUDITORÍA Y CONSULTORÍA TÉCNICA:
        1. VALIDACIÓN: ¿El N° {n_in} es correcto para un {r_in} de {v_in}?
        2. SI HAY ERROR: Como experto, identifica que el número dado NO corresponde. 
           - **INSTRUCCIÓN ESPECIAL**: Según la descripción del vehículo ({v_in}) y el nombre del repuesto ({r_in}), SUGIERE los números de parte originales (OEM) o sustitutos correctos. 
           - Di algo como: "El número ingresado no coincide, pero para su vehículo el correcto es [N° sugerido]. Por favor valide esta información y reintente."
        3. SI ES CORRECTO: Confirma la pieza y menciona si es un número sustituto o de marca genérica reconocida.

        TAREA 2: MEDIDAS PARA LOGÍSTICA:
        - Define Largo, Ancho, Alto (cm) y Peso (kg) del empaque REFORZADO para el repuesto CORRECTO (el que tú sugieres o el validado).

        RESPONDE ÚNICAMENTE CON ESTE FORMATO:
        VERDICTO: [Tu análisis técnico, sugerencias de números correctos y advertencias]
        DATOS_FISICOS: [Largo]x[Ancho]x[Alto]cm | [Peso]kg
        """

        with st.spinner('El Perito está consultando catálogos y validando números...'):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt_tecnico}]}]}, timeout=20)
                if res.status_code == 200:
                    st.session_state.raw_tecnico = res.json()['candidates'][0]['content']['parts'][0]['text']
                else: st.error("Error en el Asesor Técnico.")
            except: st.error("Sin conexión al motor de inteligencia.")
    else:
        st.warning("⚠️ Complete todos los campos.")

# 6. CEREBRO MATEMÁTICO: LÓGICA DE CÁLCULO BLINDADA (PYTHON)
if 'raw_tecnico' in st.session_state and st.session_state.raw_tecnico:
    import re
    raw = st.session_state.raw_tecnico
    
    # 1. Extracción de datos (Limpieza de seguridad)
    try:
        veredicto = re.search(r"VERDICTO: (.*)", raw).group(1)
        dims = re.findall(r"(\d+)", re.search(r"MEDIDAS_CM: (.*)", raw).group(1))
        L, An, Al = float(dims[0]), float(dims[1]), float(dims[2])
        P_real_kg = float(re.search(r"PESO_KG: ([\d.]+)", raw).group(1))
    except:
        st.error("El Asesor Técnico no entregó medidas claras. Reintente.")
        st.stop()

    # 2. Lógica de cálculo (Selección de Ruta)
    vol_cm3 = L * An * Al
    
    if o_in == "Miami" and t_in == "Marítimo":
        # MARÍTIMO: Pies Cúbicos (Fórmula: cm3 / 28316.8)
        facturable = vol_cm3 / 28316.8
        u_simbolo = "ft³"
        tarifa_v = st.session_state.tarifas['mia_m']
        costo_bruto = facturable * tarifa_v
        detalle_factura = f"{round(facturable, 2)} ft³"

    elif o_in == "Miami" and t_in == "Aéreo":
        # MIAMI AÉREO: Libras (Mayor entre kg Real y kg Volumétrico)
        p_vol_kg = vol_cm3 / 5000
        p_mayor_kg = max(P_real_kg, p_vol_kg)
        facturable_lb = p_mayor_kg * 2.20462
        u_simbolo = "lb"
        tarifa_v = st.session_state.tarifas['mia_a']
        costo_bruto = facturable_lb * tarifa_v
        detalle_factura = f"{round(facturable_lb, 2)} lb"

    else: # MADRID VENEZUELA
        # MADRID: Kilos (Mayor entre kg Real y kg Volumétrico)
        p_vol_kg = vol_cm3 / 5000
        p_mayor_kg = max(P_real_kg, p_vol_kg)
        u_simbolo = "kg"
        tarifa_v = st.session_state.tarifas['mad']
        costo_bruto = p_mayor_kg * tarifa_v
        detalle_factura = f"{round(p_mayor_kg, 2)} kg"

    # 3. Aplicación de la Regla de Oro del Mínimo
    costo_final = max(25.0, costo_bruto)
    nota_minimo = " (Tarifa mínima aplicada)" if costo_bruto < 25.0 else ""

    # --- DISEÑO DE SALIDA (Limpio y Profesional) ---
    st.markdown("---")
    st.subheader("📋 Cotización Final de Envío")
    
    res_1, res_2 = st.columns([2, 1])
    
    with res_1:
        st.markdown(f"**Análisis Técnico:**\n{veredicto}")
        st.write(f"**Configuración Logística:** {L}x{An}x{Al} cm | {P_real_kg} kg")
        st.write(f"**Cálculo:** {detalle_factura} x ${tarifa_v}")
    
    with res_2:
        st.metric("COSTO DDP", f"${costo_final:.2f}")
        if nota_minimo:
            st.warning(nota_minimo)

    if st.button("🗑️ NUEVA COTIZACIÓN"):
        st.session_state.raw_tecnico = ""
        st.rerun()

st.markdown("---")

# 7. CALCULADORA MANUAL INDEPENDIENTE (CON RESETEO A MIAMI AÉREO)
with st.expander("📊 CALCULADORA MANUAL INDEPENDIENTE"):
    st.write("Realice cálculos rápidos sin afectar la cotización de la IA.")
    
    # 7.1 INICIALIZACIÓN DE SEGURIDAD (Para evitar AttributeError)
    if 'clean_manual' not in st.session_state:
        st.session_state.clean_manual = 0
    
    # 7.2 Selectores de control propios
    c1, c2 = st.columns(2)
    with c1:
        # Miami es el índice 0
        origen_m = st.selectbox("Origen del Envío", ["Miami", "Madrid"], index=0, key=f"or_manual_{st.session_state.clean_manual}")
    with c2:
        # Lógica de envío: Aéreo es índice 0
        opciones_envio = ["Aéreo"] if origen_m == "Madrid" else ["Aéreo", "Marítimo"]
        tipo_m = st.selectbox("Tipo de Envío", opciones_envio, index=0, key=f"ti_manual_{st.session_state.clean_manual}")

    # 7.3 Campos de dimensiones
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1: l_cm = st.number_input("Largo (cm)", min_value=0.0, format="%.1f", key=f"l_{st.session_state.clean_manual}")
    with mc2: an_cm = st.number_input("Ancho (cm)", min_value=0.0, format="%.1f", key=f"an_{st.session_state.clean_manual}")
    with mc3: al_cm = st.number_input("Alto (cm)", min_value=0.0, format="%.1f", key=f"al_{st.session_state.clean_manual}")
    with mc4: p_kg_in = st.number_input("Peso Real (kg)", min_value=0.0, format="%.1f", key=f"p_{st.session_state.clean_manual}")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🧮 CALCULAR AHORA", use_container_width=True):
            vol_cm3 = l_cm * an_cm * al_cm
            
            if origen_m == "Miami" and tipo_m == "Marítimo":
                ft3 = vol_cm3 / 28316.8
                costo_base = ft3 * st.session_state.tarifas['mia_m']
                dato_facturable = f"{ft3:.2f} ft³"
                tarifa_aplicada = st.session_state.tarifas['mia_m']
            elif origen_m == "Madrid":
                p_vol = vol_cm3 / 5000
                p_mayor = max(p_kg_in, p_vol)
                costo_base = p_mayor * st.session_state.tarifas['mad']
                dato_facturable = f"{p_mayor:.2f} kg"
                tarifa_aplicada = st.session_state.tarifas['mad']
            else: # Miami Aéreo
                p_vol = vol_cm3 / 5000
                p_mayor_kg = max(p_kg_in, p_vol)
                p_libras = p_mayor_kg * 2.20462
                costo_base = p_libras * st.session_state.tarifas['mia_a']
                dato_facturable = f"{p_libras:.2f} lb"
                tarifa_aplicada = st.session_state.tarifas['mia_a']

            if costo_base < 25.0:
                total_final = 25.0
                st.warning(f"⚠️ El monto calculado (${costo_base:.2f}) no alcanza el mínimo. Se cobrarán $25.00")
            else:
                total_final = costo_base
                st.success("✅ Cálculo procesado correctamente")

            st.markdown(f"**TOTAL DDP ({origen_m} {tipo_m}): ${total_final:.2f}**")

    with col_btn2:
        if st.button("🧹 LIMPIAR TABLA", use_container_width=True):
            st.session_state.clean_manual += 1
            st.rerun()
