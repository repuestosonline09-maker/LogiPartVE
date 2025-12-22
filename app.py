import streamlit as st
import requests
import json

# 1. Configuración de pantalla y Estética
st.set_page_config(page_title="LogiParts AI", layout="wide", page_icon="📦")

st.markdown("""
    <style>
    .report-container { 
        padding: 25px; 
        border-radius: 15px; 
        background-color: #f8f9fa; 
        border: 1px solid #dee2e6; 
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        color: #1a1a1a;
        line-height: 1.6;
    }
    .stButton>button { 
        width: 100%; 
        background-color: #007bff; 
        color: white; 
        height: 3.5em; 
        font-weight: bold;
        border-radius: 10px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Sidebar para Credenciales
with st.sidebar:
    st.header("⚙️ Configuración")
    st.info("Introduce la contraseña para habilitar el campo de API Key.")
    admin_pass = st.text_input("Contraseña Admin", type="password")
    
    api_key = ""
    if admin_pass == "admin123":
        api_key = st.text_input("Pega aquí tu API Key de Google", type="password")
        if api_key:
            st.success("✅ API Key lista para usar")
    elif admin_pass:
        st.error("❌ Contraseña incorrecta")

st.title("📦 Cotizador Inteligente LogiParts")
st.markdown("### Análisis Logístico de Repuestos con Inteligencia Artificial")

# 3. Formulario de Entrada
col1, col2, col3 = st.columns(3)
with col1:
    vehiculo = st.text_input("🚙 Vehículo", placeholder="Ej: 2015 Toyota Corolla")
with col2:
    repuesto = st.text_input("🔧 Pieza", placeholder="Ej: Alternador")
with col3:
    nro_parte = st.text_input("🏷️ N° Parte", placeholder="Ej: 27060-0V020 (Opcional)")

# 4. Lógica de Petición
if st.button("GENERAR COTIZACIÓN AHORA"):
    if not api_key:
        st.error("⚠️ Error: Debes ingresar una API Key válida en el panel lateral.")
    elif not vehiculo or not repuesto:
        st.warning("⚠️ Atención: Los campos 'Vehículo' y 'Pieza' son obligatorios para el análisis.")
    else:
        try:
            # URL actualizada al modelo gemini-1.5-flash-8b (versión estable v1)
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-8b:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": (
                            f"Eres un experto en logística automotriz internacional. "
                            f"Genera un presupuesto profesional para enviar a Venezuela los siguientes datos:\n"
                            f"Vehículo: {vehiculo}\n"
                            f"Repuesto: {repuesto}\n"
                            f"Nro Parte: {nro_parte if nro_parte else 'No especificado'}\n\n"
                            f"El informe debe incluir estrictamente:\n"
                            f"1. Descripción técnica de la pieza.\n"
                            f"2. Peso estimado en libras (lb).\n"
                            f"3. Precio estimado del repuesto en el mercado de USA (USD).\n"
                            f"4. Comparativa de envío a Venezuela: Aéreo (7-10 días) vs Marítimo (3-4 semanas).\n"
                            f"Usa un tono profesional, claro y directo."
                        )
                    }]
                }]
            }
            
            headers = {'Content-Type': 'application/json'}
            
            with st.spinner('⏳ Consultando con la IA de LogiParts...'):
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                resultado = response.json()
                
            if response.status_code == 200:
                # Extraemos el contenido de la respuesta
                texto_ia = resultado['candidates'][0]['content']['parts'][0]['text']
                
                st.markdown("---")
                st.subheader("📋 Informe de Cotización Estimado")
                
                # Caja contenedora del resultado
                st.markdown(f'<div class="report-container">{texto_ia}</div>', unsafe_allow_html=True)
                
                st.success("✅ Análisis completado con éxito.")
                st.balloons()
            else:
                # Manejo de errores específicos de la API
                error_msg = resultado.get('error', {}).
