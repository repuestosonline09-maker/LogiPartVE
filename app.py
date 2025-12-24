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

# 5. MOTOR DE INTELIGENCIA (AJUSTE TÉCNICO: INTERCAMBIOS OEM/AFTERMARKET)
if st.button("🚀 GENERAR ANÁLISIS Y COTIZACIÓN PROFESIONAL", type="primary", use_container_width=True):
    if v_in and r_in and n_in:
        if o_in == "Madrid" and t_in == "Marítimo":
            st.error("⚠️ Error: Madrid solo permite envíos Aéreos.")
        else:
            # Selección de tarifa única
            if o_in == "Miami":
                tarifa_uso = st.session_state.tarifas['mia_a'] if t_in == "Aéreo" else st.session_state.tarifas['mia_m']
                unidad_uso = "Libras (lb)" if t_in == "Aéreo" else "Pies Cúbicos (ft³)"
            else:
                tarifa_uso = st.session_state.tarifas['mad']
                unidad_uso = "Kilogramos (kg)"

            prompt = f"""
            ACTÚA COMO EL EXPERTO SENIOR EN REPUESTOS AUTOMOTRICES DE LogiPartVE. 
            Tu conocimiento abarca catálogos ORIGINALES (OEM) y marcas AFTERMARKET líderes (Denso, Bosch, AC Delco, Motorcraft, KYB, etc.).

            DATOS A VALIDAR:
            - Vehículo: {v_in} | Repuesto: {r_in} | N° de Parte ingresado: {n_in}
            - Ruta: {o_in} ({t_in}) | Tarifa DDP: {tarifa_uso} por {unidad_uso}

            TAREA 1: VALIDACIÓN TÉCNICA Y CRUCE DE REFERENCIAS:
            1. Cruza el N° de parte {n_in} con el vehículo {v_in}. 
            2. Identifica si es un número Original o de una marca Aftermarket reconocida (como Denso, Bosch, etc.).
            3. Si es de una marca Aftermarket, verifica si INTERCAMBIA (Cross-Reference) con el original.
            4. Si el intercambio es válido, CONFIRMA la compatibilidad. Si es erróneo, indica el error y sugiere el OEM correcto.

            TAREA 2: LOGÍSTICA DE RUTA ÚNICA:
            - Define Largo, Ancho, Alto (cm) y Peso (kg) del empaque REFORZADO para esta pieza de forma autónoma.
            - Calcula Peso Volumétrico (LxAnxAl/5000). Usa el MAYOR entre Real y Volumétrico.
            - Calcula el costo multiplicando ÚNICAMENTE por {tarifa_uso}.
            - Miami Aéreo: lb (kg x 2.20462). Miami Marítimo: ft³ (cm3/28316.8). Madrid: kg.
            - PROHIBIDO mostrar o calcular costos de otras rutas.

            TAREA 3: REGLA DE ORO DEL MÍNIMO:
            - Si el costo total calculado es MENOR a $25.00 USD, establece el total en $25.00 USD.
            - Muestra obligatoriamente: "⚠️ Se aplica tarifa mínima de envío ($25.00)".

            RESULTADO FINAL:
            - Diagnóstico Técnico (Validación de compatibilidad e intercambio de marca).
            - Especificaciones del empaque reforzado.
            - COSTO TOTAL DDP: $XX.XX USD (Puerta a puerta, todo incluido).
            """
            
            with st.spinner('Validando pieza y calculando logística...'):
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
                    res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
                    if res.status_code == 200:
                        st.session_state.resultado_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
                        st.balloons()
                    else:
                        st.error("Error en respuesta de IA.")
                except Exception as e:
                    st.error(f"Error de conexión: {str(e)}")
    else:
        st.warning("⚠️ Complete todos los campos.")

# 6. RESULTADOS
if st.session_state.resultado_ia:
    st.info(st.session_state.resultado_ia)
    if st.button("🗑️ NUEVA CONSULTA", use_container_width=True):
        st.session_state.count += 1
        st.session_state.resultado_ia = ""
        st.rerun()

st.markdown("---")

# 7. CALCULADORA MANUAL INDEPENDIENTE (CON SELECTORES PROPIOS)
with st.expander("📊 CALCULADORA MANUAL INDEPENDIENTE"):
    st.write("Realice cálculos rápidos sin afectar la cotización de la IA.")
    
    # 7.1 Selectores de control propios de la tabla
    c1, c2 = st.columns(2)
    with c1:
        origen_m = st.selectbox("Origen del Envío", ["Miami", "Madrid"], key="origen_manual")
    with c2:
        # Si es Madrid, solo permitimos Aéreo por lógica de negocio
        opciones_envio = ["Aéreo"] if origen_m == "Madrid" else ["Aéreo", "Marítimo"]
        tipo_m = st.selectbox("Tipo de Envío", opciones_envio, key="tipo_manual")

    # 7.2 Campos de dimensiones
    if 'clean_manual' not in st.session_state:
        st.session_state.clean_manual = 0

    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1: l_cm = st.number_input("Largo (cm)", min_value=0.0, format="%.1f", key=f"l_{st.session_state.clean_manual}")
    with mc2: an_cm = st.number_input("Ancho (cm)", min_value=0.0, format="%.1f", key=f"an_{st.session_state.clean_manual}")
    with mc3: al_cm = st.number_input("Alto (cm)", min_value=0.0, format="%.1f", key=f"al_{st.session_state.clean_manual}")
    with mc4: p_kg_in = st.number_input("Peso Real (kg)", min_value=0.0, format="%.1f", key=f"p_{st.session_state.clean_manual}")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🧮 CALCULAR AHORA", use_container_width=True):
            vol_cm3 = l_cm * an_cm * al_cm
            
            # LÓGICA INDEPENDIENTE POR RUTA
            if origen_m == "Miami" and tipo_m == "Marítimo":
                # Marítimo: Pies Cúbicos
                ft3 = vol_cm3 / 28316.8
                costo_base = ft3 * st.session_state.tarifas['mia_m']
                dato_facturable = f"{ft3:.2f} ft³"
                tarifa_aplicada = st.session_state.tarifas['mia_m']
            
            elif origen_m == "Madrid":
                # Madrid: Kilos (Mayor entre Real y Volumétrico)
                p_vol = vol_cm3 / 5000
                p_mayor = max(p_kg_in, p_vol)
                costo_base = p_mayor * st.session_state.tarifas['mad']
                dato_facturable = f"{p_mayor:.2f} kg"
                tarifa_aplicada = st.session_state.tarifas['mad']
            
            else: # Miami Aéreo
                # Miami Aéreo: Libras (Mayor entre Real y Volumétrico)
                p_vol = vol_cm3 / 5000
                p_mayor_kg = max(p_kg_in, p_vol)
                p_libras = p_mayor_kg * 2.20462
                costo_base = p_libras * st.session_state.tarifas['mia_a']
                dato_facturable = f"{p_libras:.2f} lb"
                tarifa_aplicada = st.session_state.tarifas['mia_a']

            # VALIDACIÓN DE TARIFA MÍNIMA
            if costo_base < 25.0:
                total_final = 25.0
                st.warning(f"⚠️ El monto calculado (${costo_base:.2f}) no alcanza el mínimo. Se cobrarán $25.00")
            else:
                total_final = costo_base
                st.success("✅ Cálculo procesado correctamente")

            st.markdown(f"""
            **RESULTADO DE OPERACIÓN:**
            * **Ruta:** {origen_m} vía {tipo_m}
            * **Tarifa base:** ${tarifa_aplicada}
            * **Medida Facturable:** {dato_facturable}
            * **TOTAL DDP:** ${total_final:.2f}
            """)

    with col_btn2:
        if st.button("🧹 LIMPIAR TABLA", use_container_width=True):
            st.session_state.clean_manual += 1
            st.rerun()
