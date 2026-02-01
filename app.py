import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="TechLogistics | Senior Consultant Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PLACEHOLDER FOR MODULE IMPORTS ---
# In the future, you will uncomment these:
# from src import data_loader, quality_manager, business_logic, ai_agent

# --- CSS STYLING (Optional: Professional Look) ---
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: GLOBAL CONTROLS  ---
with st.sidebar:
    st.title("🔧 TechLogistics DSS")
    st.markdown("---")
    
    st.subheader("1. Ingesta de Datos")
    # File Uploader for the 3 specific files [cite: 12, 13, 16]
    uploaded_inv = st.file_uploader("Inventario (CSV)", type="csv")
    uploaded_trans = st.file_uploader("Transacciones (CSV)", type="csv")
    uploaded_feed = st.file_uploader("Feedback (CSV)", type="csv")

    st.markdown("---")
    
    # Global filters are only active if data is loaded
    st.subheader("2. Filtros Globales")
    # These would populate dynamically based on the dataframe later
    selected_region = st.multiselect("Región / Bodega", ["Norte", "Sur", "Centro", "Occidente"])
    selected_date_range = st.date_input("Periodo de Análisis", [])

# --- MAIN LAYOUT ---
st.title("📊 TechLogistics: Data Strategy Dashboard")
st.markdown("""
> **Resumen Ejecutivo:** Dashboard de soporte a la decisión para la recuperación de margen 
> y lealtad de clientes. [cite: 9]
""")

# Check if files are uploaded before showing the main tabs
if not (uploaded_inv and uploaded_trans and uploaded_feed):
    st.info("👋 Por favor, cargue los tres archivos CSV en el panel lateral para iniciar la auditoría.")
    st.stop()

# --- TABS FOR PROJECT PHASES  ---
tab_audit, tab_business, tab_ai = st.tabs([
    "🏥 Fase 1: Auditoría & Limpieza",
    "📈 Fase 2: Business Insights",
    "🤖 Fase 3: Consultor IA (Groq)"
])

# ==============================================================================
# TAB 1: DATA HEALTH & CLEANING [cite: 18]
# ==============================================================================
with tab_audit:
    st.header("1. Auditoría de Calidad y Transparencia")
    
    col_audit_left, col_audit_right = st.columns([1, 2])
    
    # --- Left: Cleaning Parameters (User Control) ---
    with col_audit_left:
        st.subheader("⚙️ Configuración de Limpieza")
        st.write("Defina las reglas éticas para el tratamiento de datos:")
        
        # 1. Outlier Strategy [cite: 15, 20]
        st.markdown("**1. Tratamiento de Outliers (Tiempos de Entrega)**")
        outlier_method = st.radio(
            "Método de detección:",
            ["Rango Intercuartil (IQR)", "Z-Score (Desviación Estándar)"]
        )
        if outlier_method == "Z-Score (Desviación Estándar)":
            sigma_threshold = st.slider("Umbral Sigma", 1.0, 4.0, 3.0)
        
        # 2. Null Strategy [cite: 21]
        st.markdown("**2. Imputación de Valores Nulos**")
        fill_strategy = st.selectbox(
            "Estrategia para Costos/Precios faltantes:",
            ["Usar la Media", "Usar la Mediana", "Eliminar Registros"]
        )
        
        # 3. Ghost SKUs Strategy [cite: 28]
        st.markdown("**3. Ventas sin Inventario (Ghost SKUs)**")
        ghost_action = st.radio(
            "Acción para SKUs huérfanos:",
            ["Conservar (Marcar como riesgo)", "Eliminar del análisis financiero"]
        )

        btn_run_cleaning = st.button("🔄 Ejecutar Limpieza y Calcular Health Score")

    # --- Right: Results & Health Score ---
    with col_audit_right:
        if btn_run_cleaning:
            st.success("¡Limpieza Ejecutada Exitosamente!")
            
            # Placeholder Metrics: Before vs After [cite: 19]
            m1, m2, m3 = st.columns(3)
            m1.metric("Filas Originales", "17,000", "0")
            m2.metric("Filas Limpias", "16,450", "-550 (3.2%)")
            m3.metric("Health Score Global", "92/100", "+15 pts")
            
            # Detailed Health Report Expander
            with st.expander("Ver Reporte Detallado de Anomalías"):
                st.write("Aquí se mostrarán los duplicados eliminados y outliers detectados.")
            
            # Download Button 
            st.download_button(
                label="📥 Descargar Datos Limpios (.csv)",
                data="sample_data", # Replace with actual CSV string
                file_name="techlogistics_clean_data.csv",
                mime="text/csv"
            )
        else:
            st.info("Presione 'Ejecutar Limpieza' para ver el diagnóstico.")

# ==============================================================================
# TAB 2: BUSINESS INSIGHTS (The 5 Questions) [cite: 33]
# ==============================================================================
with tab_business:
    st.header("2. Tablero de Control Estratégico")
    
    # Section 1: Financials [cite: 37, 41]
    st.subheader("💰 Fuga de Capital & Rentabilidad")
    b1, b2 = st.columns(2)
    with b1:
        st.markdown("**Pregunta 1: SKUs con Margen Negativo**")
        st.write("[GRÁFICO: Barra de Top SKUs con pérdidas]")
    with b2:
        st.markdown("**Pregunta 3: Impacto Ventas Invisibles**")
        st.metric("Pérdida por Descontrol de Inventario", "$124,500 USD", delta="-12%", delta_color="inverse")

    st.divider()

    # Section 2: Logistics & Operations [cite: 39, 45]
    st.subheader("🚚 Operaciones y Logística")
    b3, b4 = st.columns(2)
    with b3:
        st.markdown("**Pregunta 2: Correlación Tiempos vs. NPS**")
        st.write("[GRÁFICO: Heatmap de Bodegas]")
    with b4:
        st.markdown("**Pregunta 5: Riesgo Operativo (Stock vs. Soporte)**")
        st.write("[GRÁFICO: Scatter Plot Antigüedad vs Tickets]")
        
    st.divider()
    
    # Section 3: Customer Fidelity [cite: 43]
    st.subheader("❤️ Diagnóstico de Fidelidad")
    st.markdown("**Pregunta 4: Paradoja de Disponibilidad vs. Sentimiento**")
    st.write("[GRÁFICO: Scatter Categorías (Stock Alto / NPS Bajo)]")

# ==============================================================================
# TAB 3: AI CONSULTANT (Groq) [cite: 31]
# ==============================================================================
with tab_ai:
    st.header("3. Asistente Estratégico (Powered by Llama-3)")
    
    st.markdown("""
    Este módulo analiza el resumen estadístico de los datos filtrados y genera 
    recomendaciones estratégicas en tiempo real. [cite: 32]
    """)
    
    # Context Display
    st.info(f"Contexto actual: Análisis basado en {len(selected_region)} regiones seleccionadas.")
    
    # User Input
    user_query = st.text_area(
        "📝 Pregunta a la Junta Directiva Digital:", 
        placeholder="Ej: ¿Qué estrategia sugerimos para reducir la fuga de capital en la zona Norte?"
    )
    
    if st.button("🤖 Generar Estrategia"):
        with st.spinner("Consultando con el modelo Llama-3 en Groq..."):
            # Mock response for structure
            st.markdown("### Recomendación Estratégica")
            st.markdown("""
            **1. Optimización de Inventario:** Se detectó que el 15% de las pérdidas provienen de SKUs fantasmas...
            
            **2. Acción Logística:** La bodega 'Norte' presenta tiempos de entrega superiores a 10 días...
            
            **3. Fidelización:** Implementar política de devoluciones para productos con NPS < 3...
            """)