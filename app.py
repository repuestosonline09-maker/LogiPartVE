import streamlit as st
import google.generativeai as genai
import json
import time

# ==========================================
# 1. CONFIGURACIÓN DEL EXPERTO (EL CEREBRO)
# ==========================================

st.set_page_config(page_title="LogiParts AI", page_icon="🚛", layout="centered")

# PROMPT MAESTRO: AQUÍ ESTÁ TU PERSONALIDAD Y REGLAS
SYSTEM_PROMPT = """
ACTÚA COMO UN EXPERTO MUNDIAL EN LOGÍSTICA DE AUTOPARTES Y ENVÍOS INTERNACIONALES.
Tu misión es validar piezas y estimar sus dimensiones de embalaje PARA EXPORTACIÓN (Reforzado).

ENTRADAS: Vehículo, Nombre Pieza, Número de Parte.

TUS REGLAS DE PENSAMIENTO (CRÍTICO):
1. VALIDACIÓN CRUZADA: Verifica si el Número de Parte corresponde realmente a la Pieza y al Vehículo descritos.
   - Si es totalmente incompatible (ej. Parte de Toyota para un Ford), marca ERROR_CRUZADO.
   - Si el número es desconocido pero la descripción es clara, usa tu criterio experto para estimar por similitud (STATUS: ESTIMADO).
2. SUPERSESSION (SUSTITUCIONES): Si el número es viejo, identifica el reemplazo moderno y cotiza con ese (STATUS: OK_SUSTITUTO).
3. EMBALAJE: No des medidas de la pieza desnuda. Calcula medidas con CAJA REFORZADA, MADERA o CRATE según requiera la pieza para soportar trato rudo marítimo.
4. SEGURIDAD: Si es Material Peligroso (Amortiguadores con gas, Airbags, Baterías), avisa en el campo 'advertencia'.

FORMATO DE RESPUESTA OBLIGATORIO (SOLO JSON):
Debes responder ÚNICAMENTE con un JSON válido con esta estructura exacta, sin texto antes ni después:
{
    "status": "OK" | "OK_SUSTITUTO" | "ESTIMADO" | "ERROR_CRUZADO" | "UNKNOWN",
    "mensaje": "Explicación breve para el vendedor",
    "peso_lb": 0.0,
    "largo_cm": 0.0,
    "ancho_cm": 0.0,
    "alto_cm": 0.0,
    "advertencia": "Texto de alerta DG o vacío",
    "nuevo_numero_parte": "Solo si aplica sustitución"
}
"""

# ==========================================
# 2. FUNCIONES DE LÓGICA
# ==========================================

def consultar_ia(api_key, vehiculo, pieza, parte):
    try:
        genai.configure(api_key=api_key, transport='rest')
        model = genai.GenerativeModel('gemini-1.5-flash') # Modelo rápido y eficiente
        
        consulta = f"""
        SOLICITUD DE COTIZACIÓN:
        - Vehículo: {vehiculo}
        - Pieza: {pieza}
        - Número de Parte (Input): {parte}
        
        Analiza, valida y genera el JSON de dimensiones de envío.
        """
        
        response = model.generate_content(SYSTEM_PROMPT + consulta)
        
        # Limpieza para asegurar JSON puro
        texto_limpio = response.text.replace("```json", "").replace("```", "").strip()
        datos = json.loads(texto_limpio)
        return datos
        
    except Exception as e:
        return {"status": "ERROR_TECNICO", "mensaje": f"Error de conexión: {str(e)}"}

def calcular_costos(peso, l, w, h, tarifas):
    # Buffer de seguridad (Margen de error del Admin)
    buffer = 1 + (tarifas['buffer'] / 100)
    l, w, h = l * buffer, w * buffer, h * buffer
    
    # Fórmulas
    vol_kg = (l * w * h) / 6000
    vol_lb_aereo = vol_kg * 2.20462
    peso_tasable_aereo = max(peso, vol_lb_aereo)
    
    ft3 = ((l * w * h) / 1000000) * 35.3147
    
    costo_aereo = peso_tasable_aereo * tarifas['aereo']
    costo_maritimo = max(ft3 * tarifas['maritimo'], tarifas['minimo_maritimo'])
    
    return {
        "aereo": costo_aereo,
        "peso_tasable": peso_tasable_aereo,
        "maritimo": costo_maritimo,
        "ft3": ft3,
        "es_minimo": costo_maritimo == tarifas['minimo_maritimo']
    }

# ==========================================
# 3. INTERFAZ DE USUARIO (STREAMLIT)
# ==========================================

# --- INICIALIZACIÓN DE VARIABLES ---
if 'config' not in st.session_state:
    st.session_state['config'] = {
        'aereo': 9.00,
        'maritimo': 40.00,
        'minimo_maritimo': 40.00,
        'buffer': 5, # 5% extra por seguridad
        'api_key': '' # Aquí se guardará la llave
    }

# --- BARRA LATERAL (ADMIN) ---
with st.sidebar:
    st.title("⚙️ Admin Panel")
    clave = st.text_input("Contraseña Admin", type="password")
    
    if clave == "admin123": # PUEDES CAMBIAR ESTA CLAVE
        st.success("Modo Editor Activo")
        st.markdown("### 🔑 Llave Maestra")
        st.session_state['config']['api_key'] = st.text_input("Pega tu Google API Key aquí:", value=st.session_state['config']['api_key'], type="password")
        
        st.markdown("### 💰 Tarifas")
        st.session_state['config']['aereo'] = st.number_input("Aéreo ($/lb)", value=st.session_state['config']['aereo'])
        st.session_state['config']['maritimo'] = st.number_input("Marítimo ($/ft³)", value=st.session_state['config']['maritimo'])
        st.session_state['config']['minimo_maritimo'] = st.number_input("Mínimo Marítimo ($)", value=st.session_state['config']['minimo_maritimo'])
        st.session_state['config']['buffer'] = st.slider("Margen Seguridad (%)", 0, 20, st.session_state['config']['buffer'])
    else:
        st.info("Ingresa clave para configurar tarifas y API.")

# --- PANTALLA PRINCIPAL ---
st.title("🚛 LogiParts AI")
st.markdown("**Cotizador Inteligente de Autopartes** | *Powered by Gemini Expert*")

if not st.session_state['config']['api_key']:
    st.warning("⚠️ ALERTA: El sistema no tiene la API Key configurada. Por favor contacta al administrador.")
    st.stop()

# FORMULARIO
col1, col2 = st.columns(2)
with col1:
    origen = st.selectbox("📍 Origen", ["Miami (USA)", "Madrid (Europa)"])
    vehiculo = st.text_input("🚗 Vehículo", placeholder="Ej: Ford Explorer 2015 3.5L")
with col2:
    pieza = st.text_input("🔧 Pieza", placeholder="Ej: Alternador")
    parte = st.text_input("🔢 N° Parte", placeholder="Ej: BA5Z-1234-A")

# BOTÓN DE ACCIÓN
if st.button("🚀 COTIZAR AHORA", type="primary"):
    if not vehiculo or not pieza:
        st.error("Faltan datos obligatorios.")
    else:
        with st.spinner('🤖 Analizando pieza, cruzando referencias y calculando embalaje...'):
            # LLAMADA A LA IA REAL
            datos_ia = consultar_ia(st.session_state['config']['api_key'], vehiculo, pieza, parte)
        
        # DECISIÓN BASADA EN RESPUESTA
        mostrar_resultados = False
        usar_manual = False
        
        if datos_ia['status'] in ["OK", "OK_SUSTITUTO", "ESTIMADO"]:
            mostrar_resultados = True
            if datos_ia['status'] == "OK_SUSTITUTO":
                st.info(f"🔄 **CAMBIO DETECTADO:** N° de parte antiguo. Cotizando con sustituto: **{datos_ia.get('nuevo_numero_parte')}**")
            elif datos_ia['status'] == "ESTIMADO":
                st.warning(f"⚠️ **ESTIMACIÓN:** {datos_ia['mensaje']}")
        else:
            # ERRORES O DESCONOCIDOS
            st.error(f"🛑 **ALERTA:** {datos_ia['mensaje']}")
            usar_manual = True

        # SI LA IA FALLÓ, OFRECER MANUAL
        if usar_manual:
            with st.expander("📝 **¿Tienes las medidas? Cotizar Manualmente**", expanded=True):
                c1, c2, c3, c4 = st.columns(4)
                m_lb = c1.number_input("Peso (Lb)", 1.0)
                m_l = c2.number_input("Largo (cm)", 10.0)
                m_w = c3.number_input("Ancho (cm)", 10.0)
                m_h = c4.number_input("Alto (cm)", 10.0)
                if st.button("Calcular Manual"):
                    datos_ia = {'peso_lb': m_lb, 'largo_cm': m_l, 'ancho_cm': m_w, 'alto_cm': m_h, 'advertencia': ''}
                    mostrar_resultados = True

        # MOSTRAR TARJETAS DE PRECIO
        if mostrar_resultados:
            res = calcular_costos(datos_ia['peso_lb'], datos_ia['largo_cm'], datos_ia['ancho_cm'], datos_ia['alto_cm'], st.session_state['config'])
            
            st.markdown("---")
            if datos_ia.get('advertencia'):
                st.error(f"🔥 **MERCANCÍA PELIGROSA:** {datos_ia['advertencia']}")

            c_res1, c_res2 = st.columns(2)
            
            # TARJETA AÉREA
            with c_res1:
                st.markdown(f"""
                <div style="background-color:#f8f9fa;padding:15px;border-radius:10px;border-left:5px solid #0d6efd">
                    <h3 style="margin:0;color:#0d6efd">✈️ AÉREO</h3>
                    <h1 style="margin:0">${res['aereo']:.2f}</h1>
                    <small>Peso Tasable: {res['peso_tasable']:.1f} lbs</small>
                </div>
                """, unsafe_allow_html=True)

            # TARJETA MARÍTIMA
            with c_res2:
                color_borde = "#198754" if res['es_minimo'] else "#ffc107"
                aviso_minimo = "<br><b>(Aplica Mínimo)</b>" if res['es_minimo'] else ""
                st.markdown(f"""
                <div style="background-color:#f8f9fa;padding:15px;border-radius:10px;border-left:5px solid {color_borde}">
                    <h3 style="margin:0;color:{color_borde}">🚢 MARÍTIMO</h3>
                    <h1 style="margin:0">${res['maritimo']:.2f}</h1>
                    <small>Volumen: {res['ft3']:.2f} ft³ {aviso_minimo}</small>
                </div>
                """, unsafe_allow_html=True)
                
                if res['es_minimo'] and res['ft3'] < 0.8:
                     st.info("💡 **CONSEJO:** Tienes espacio libre en la caja. ¡Mete filtros o bujías sin costo extra!")
            
            with st.expander("🔍 Ver detalles técnicos del paquete"):
                st.write(f"Dimensiones calculadas: {datos_ia['largo_cm']} x {datos_ia['ancho_cm']} x {datos_ia['alto_cm']} cm")
                st.write(f"Peso Físico: {datos_ia['peso_lb']} lb")
