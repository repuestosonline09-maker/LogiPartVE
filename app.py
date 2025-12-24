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

# 5. CEREBRO TÉCNICO: EL ASESOR EXPERTO (REFORZADO)
if st.button("🚀 GENERAR ANÁLISIS TÉCNICO", type="primary", use_container_width=True):
    if v_in and r_in and n_in:
        prompt_tecnico = f"""
        ERES EL PERITO TÉCNICO SENIOR DE LogiPartVE. 
        TU MISIÓN: VALIDAR COMPATIBILIDAD Y ENTREGAR MEDIDAS PARA CÁLCULO.

        DATOS: {r_in} | {n_in} | {v_in}.

        TAREA:
        1. VALIDA el N° {n_in}. Si es incorrecto, SUGIERE el OEM correcto para {v_in}.
        2. ESTIMA medidas de empaque reforzado (L, An, Al en cm) y peso (kg).

        DEBES RESPONDER SIGUIENDO ESTE FORMATO EXACTO (SIN TEXTO EXTRA AL FINAL):
        VERDICTO: [Tu análisis técnico y sugerencias aquí]
        DATOS_FISICOS: [Largo]x[Ancho]x[Alto]cm | [Peso]kg
        """

        with st.spinner('Auditando en catálogos...'):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt_tecnico}]}]}, timeout=20)
                if res.status_code == 200:
                    st.session_state.raw_tecnico = res.json()['candidates'][0]['content']['parts'][0]['text']
                else: st.error("Error en el API.")
            except: st.error("Error de conexión.")
    else:
        st.warning("⚠️ Complete todos los campos.")

# 6. CEREBRO MATEMÁTICO (EXTRACCIÓN FLEXIBLE)
if 'raw_tecnico' in st.session_state and st.session_state.raw_tecnico:
    import re
    raw = st.session_state.raw_tecnico
    
    try:
        # Buscamos el veredicto
        veredicto_match = re.search(r"VERDICTO:\s*(.*)", raw, re.IGNORECASE)
        veredicto = veredicto_match.group(1) if veredicto_match else "Análisis disponible."
        
        # Buscamos la línea de datos físicos y extraemos todos los números encontrados en ella
        datos_linea = re.search(r"DATOS_FISICOS:\s*(.*)", raw, re.IGNORECASE).group(1)
        numeros = re.findall(r"[\d.]+", datos_linea)
        
        # Asignamos: Largo, Ancho, Alto, Peso
        L = float(numeros[0])
        An = float(numeros[1])
        Al = float(numeros[2])
        P_fisico = float(numeros[3])
        
        # --- Lógica de cálculo (La misma que ya perfeccionamos) ---
        vol_cm3 = L * An * Al
        if o_in == "Miami" and t_in == "Marítimo":
            facturable = vol_cm3 / 28316.8
            tarifa_v = st.session_state.tarifas['mia_m']
            u = "ft³"
        elif o_in == "Miami" and t_in == "Aéreo":
            p_vol = vol_cm3 / 5000
            facturable = max(P_fisico, p_vol) * 2.20462
            tarifa_v = st.session_state.tarifas['mia_a']
            u = "lb"
        else: # Madrid
            p_vol = vol_cm3 / 5000
            facturable = max(P_fisico, p_vol)
            tarifa_v = st.session_state.tarifas['mad']
            u = "kg"

        costo_final = max(25.0, facturable * tarifa_v)

        # --- DISEÑO DE SALIDA PROFESIONAL ---
        st.markdown("---")
        
        # Título con icono de seguridad
        st.markdown("### 🔍 INFORME DE AUDITORÍA Y COTIZACIÓN")

        # RECUADRO DE RESALTE PARA EL ASESOR (Cerebro 1)
        with st.container(border=True):
            st.markdown("##### 🛠️ Diagnóstico del Asesor Técnico")
            st.info(veredicto) # El texto del asesor aparece en un recuadro azul profesional

        # BLOQUE DE COSTOS Y LOGÍSTICA (Cerebro 2)
        c1, c2 = st.columns([1.5, 1])
        
        with c1:
            st.markdown("##### 📦 Configuración Logística")
            st.write(f"**Empaque:** {L} x {An} x {Al} cm")
            st.write(f"**Peso Físico:** {P_fisico} kg")
            st.write(f"**Cálculo:** {round(facturable, 2)} {u} x ${tarifa_v}")
        
        with c2:
            st.markdown("##### 💰 Inversión DDP")
            st.metric(label="TOTAL A PAGAR", value=f"${round(costo_final, 2)} USD")
            if costo_bruto < 25.0:
                st.caption("⚠️ Incluye tarifa mínima de gestión")

        st.markdown(f"*(Operación puerta a puerta vía {o_in} {t_in} sin cargos ocultos)*")

    except Exception as e:
        st.error(f"⚠️ Error de lectura: El Asesor Técnico entregó un formato inesperado. (Detalle: {e})")
        
        c1, c2 = st.columns(2)
        c1.write(f"**Detalle Físico:** {L}x{An}x{Al} cm | {P_fisico} kg")
        c1.write(f"**Facturable:** {round(facturable, 2)} {u}")
        c2.metric("TOTAL DDP", f"${round(costo_final, 2)} USD")
        
    except Exception as e:
        st.error(f"⚠️ Error de lectura: La IA cambió el formato. Intente de nuevo. (Detalle: {e})")

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
