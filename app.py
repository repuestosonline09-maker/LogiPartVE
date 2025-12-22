import streamlit as st
import google.generativeai as genai

# 1. Configuración de pantalla
st.set_page_config(page_title="LogiParts AI", layout="wide")

# 2. Sidebar y Conexión
with st.sidebar:
    st.header("⚙️ Configuración")
    admin_pass = st.text_input("Contraseña Admin", type="password")
    api_key = ""
    if admin_pass == "admin123":
        api_key = st.text_input("Pega tu nueva API Key aquí", type="password")
        if api_key:
            genai.configure(api_key=api_key)
            st.success("✅ API Conectada")

st.title("📦 Cotizador LogiParts AI")

# 3. Formulario
col1, col2 = st.columns(2)
with col1:
    vehiculo = st.text_input("Vehículo", placeholder="Ej: 1985 Ford Granada")
with col2:
    repuesto = st.text_input("Pieza", placeholder="Ej: Motor de arranque")

# 4. Lógica de Cotización Simplificada
if st.button("COTIZAR AHORA"):
    if not api_key:
        st.error("⚠️ Falta la API Key en el panel lateral")
    else:
        try:
            # Usamos el nombre de modelo más compatible
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Actúa como experto en logística. Para el repuesto: {repuesto} de un {vehiculo}:
            1. Da un análisis técnico breve.
            2. Estima el peso en libras.
            3. Calcula costo de envío AÉREO y MARÍTIMO a Venezuela.
            Responde de forma clara y organizada.
            """
            
            with st.spinner('Calculando logística...'):
                response = model.generate_content(prompt)
                
            st.markdown("### 📊 Resultado de la Cotización")
            st.write(response.text)
            st.balloons()

        except Exception as e:
            st.error(f"Hubo un detalle técnico: {e}")
            st.info("Prueba refrescando la página y pegando la llave nuevamente.")
