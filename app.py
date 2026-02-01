import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="TechLogistics | Senior Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- 2. FUNCIÓN DE DATOS DE PRUEBA (MOCK DATA) ---
# Genera datos falsos para que la app funcione sin archivos CSV
@st.cache_data
def load_mock_data():
    # 1. Mock Inventario
    df_inv = pd.DataFrame({
        'SKU': [f'PROD-{i:03d}' for i in range(100)],
        'Costo': np.random.uniform(10, 100, 100),
        'Stock': np.random.randint(-5, 200, 100) # Stock negativo para simular error
    })
    
    # 2. Mock Transacciones (con SKUs fantasmas)
    # Generamos ventas de SKUs que van hasta el 110 (los del 100 al 110 no existen en inventario)
    df_trans = pd.DataFrame({
        'ID_Venta': range(1000),
        'SKU': [f'PROD-{np.random.randint(0, 110):03d}' for _ in range(1000)], 
        'Precio_Venta': np.random.uniform(20, 150, 1000),
        'Dias_Entrega': np.concatenate([np.random.normal(5, 2, 950), [999]*50]), # Outliers de 999
        'Fecha': pd.date_range(start='2025-01-01', periods=1000)
    })
    
    # 3. Mock Feedback
    df_feed = pd.DataFrame({
        'ID_Cliente': range(500),
        'NPS': np.random.randint(0, 11, 500), # NPS de 0 a 10
        'Region': np.random.choice(['Norte', 'Sur', 'Centro', 'Occidente'], 500)
    })
    
    return df_inv, df_trans, df_feed

# --- 3. SIDEBAR (CONTROLES) ---
with st.sidebar:
    st.title("🔧 TechLogistics DSS")
    st.info("💡 Modo Demostración: Usando datos generados automáticamente.")
    
    # Simulación de carga de archivos
    st.subheader("1. Ingesta de Datos")
    st.caption("Archivos cargados virtualmente...")
    
    st.markdown("---")
    
    # Filtros simulados
    st.subheader("2. Filtros Globales")
    region = st.multiselect("Región", ['Norte', 'Sur', 'Centro', 'Occidente'], default=['Norte'])
    
    st.markdown("---")
    st.caption("TechLogistics S.A.S. - Módulo de Auditoría")

# Cargar los datos simulados
df_inv, df_trans, df_feed = load_mock_data()

# --- 4. LAYOUT PRINCIPAL ---
st.title("📊 TechLogistics: Data Strategy Dashboard")
st.markdown("""
> **Resumen Ejecutivo:** Dashboard de soporte a la decisión para la recuperación de margen 
> y lealtad de clientes.
""")

# Definir las 3 pestañas principales
tab1, tab2, tab3 = st.tabs([
    "🏥 Fase 1: Auditoría & Limpieza", 
    "📈 Fase 2: Business Insights", 
    "🤖 Fase 3: IA Consultant"
])

# ==============================================================================
# TAB 1: AUDITORÍA (Interactiva)
# ==============================================================================
with tab1:
    st.header("1. Auditoría de Calidad y Transparencia")
    
    col1, col2 = st.columns([1, 2])
    
    # --- Columna Izquierda: Controles ---
    with col1:
        st.subheader("⚙️ Configuración de Limpieza")
        st.write("Defina las reglas éticas para el tratamiento de datos:")
        
        clean_mode = st.radio("Modo de Limpieza", ["Estándar (Recomendado)", "Personalizado"])
        
        outlier_threshold = st.slider(
            "Umbral de Outliers (Días de Entrega)", 
            min_value=10, max_value=100, value=30,
            help="Cualquier entrega superior a este valor se considera un error."
        )
        
        # Estado de la limpieza (Session State)
        if 'cleaned' not in st.session_state:
            st.session_state.cleaned = False
            
        if st.button("🔄 Ejecutar Limpieza"):
            with st.spinner("Limpiando duplicados, imputando nulos y eliminando outliers..."):
                time.sleep(1.5) # Simular tiempo de proceso
                st.session_state.cleaned = True
                
    # --- Columna Derecha: Resultados ---
    with col2:
        st.subheader("Diagnóstico de Salud (Health Score)")
        
        # Métricas dinámicas
        m1, m2, m3 = st.columns(3)
        
        if st.session_state.cleaned:
            # Mostrar resultados DESPUÉS de limpiar
            m1.metric("Registros Totales", "2,450", "-50 (Eliminados)", delta_color="inverse")
            m2.metric("Outliers Críticos", "0", "-50 Corregidos", delta_color="inverse")
            m3.metric("Health Score", "98/100", "+33 pts")
            
            st.success("✅ Datos limpios correctamente. Listos para análisis estratégico.")
            
            # Gráfico comparativo Antes vs Después
            health_data = pd.DataFrame({
                'Estado': ['Crudo (Raw)', 'Limpio (Clean)'],
                'Score': [65, 98]
            })
            fig_health = px.bar(health_data, x='Estado', y='Score', color='Estado', 
                                range_y=[0, 100], title="Mejora en Calidad de Datos")
            st.plotly_chart(fig_health, use_container_width=True)
            
        else:
            # Mostrar estado INICIAL
            m1.metric("Registros Totales", "2,500", "Datos Crudos")
            m2.metric("Outliers Críticos", "50", "Detectados (999 días)", delta_color="inverse")
            m3.metric("Health Score", "65/100", "Riesgo Alto", delta_color="inverse")
            
            st.warning("⚠️ Se han detectado inconsistencias graves en los tiempos de entrega y costos.")

# ==============================================================================
# TAB 2: BUSINESS INSIGHTS (Gráficos)
# ==============================================================================
with tab2:
    st.header("2. Tablero de Control Estratégico")
    
    # Fila 1: Finanzas y Logística
    row1_1, row1_2 = st.columns(2)
    
    with row1_1:
        st.subheader("💰 Fuga de Capital")
        st.markdown("**Pregunta 1: SKUs con Margen Negativo**")
        
        # Simular cálculo de pérdidas
        loss_data = pd.DataFrame({
            'SKU': ['PROD-099', 'PROD-015', 'PROD-042', 'PROD-007', 'PROD-088'],
            'Pérdida_USD': [-5400, -3200, -1500, -900, -450]
        })
        
        fig_loss = px.bar(loss_data, x='SKU', y='Pérdida_USD', color='Pérdida_USD', 
                          color_continuous_scale='reds', title="Top 5 SKUs con mayor pérdida")
        st.plotly_chart(fig_loss, use_container_width=True)
        st.caption("Alerta: Estos 5 productos representan el 80% de la fuga de margen.")

    with row1_2:
        st.subheader("🚚 Crisis Logística")
        st.markdown("**Pregunta 2: Tiempos de Entrega vs Satisfacción (NPS)**")
        
        # Simular correlación
        scatter_data = pd.DataFrame({
            'Dias_Entrega': np.random.randint(1, 40, 100),
            'NPS': np.random.randint(0, 11, 100)
        })
        # Forzar correlación visual: más días -> menos NPS
        scatter_data['NPS'] = 10 - (scatter_data['Dias_Entrega'] / 4).astype(int)
        scatter_data['NPS'] = scatter_data['NPS'].clip(0, 10)
        
        fig_scatter = px.scatter(scatter_data, x='Dias_Entrega', y='NPS', 
                                 color='NPS', color_continuous_scale='rdylgn',
                                 title="Correlación: Demoras vs Lealtad")
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.caption("Los clientes castigan severamente el NPS después de 10 días de espera.")

    st.divider()
    
    # Fila 2: Ventas Invisibles
    st.subheader("👻 Análisis de Ventas Invisibles")
    col_ghost_1, col_ghost_2 = st.columns([1, 3])
    
    with col_ghost_1:
        st.metric("Ventas 'Ghost SKU'", "$124,500 USD", delta="-12% vs mes anterior", delta_color="inverse")
        st.markdown("**Impacto:** Estas son ventas de productos que NO existen en el maestro de inventarios.")
    
    with col_ghost_2:
        # Gráfico de pastel simulado
        pie_data = pd.DataFrame({
            'Tipo': ['Venta Normal', 'Venta Ghost (Sin SKU)'],
            'Valor': [850000, 124500]
        })
        fig_pie = px.pie(pie_data, values='Valor', names='Tipo', title="Proporción de Ingresos en Riesgo")
        st.plotly_chart(fig_pie, use_container_width=True)

# ==============================================================================
# TAB 3: IA CONSULTANT (Simulación)
# ==============================================================================
with tab3:
    st.header("3. Asistente Estratégico (Powered by Llama-3)")
    
    st.markdown("""
    Este módulo utiliza IA para analizar los hallazgos de las pestañas anteriores y sugerir acciones.
    """)
    
    # Input del usuario
    query = st.text_area("📝 Pregunta a la IA:", placeholder="Ej: ¿Qué estrategia sugerimos para reducir la fuga de capital en la zona Norte?", height=100)
    
    if st.button("🤖 Generar Estrategia"):
        with st.spinner("Consultando con el modelo Llama-3 en Groq..."):
            time.sleep(2) # Simular retardo de API
            
            st.markdown("### 🧠 Recomendación Estratégica Generada:")
            st.success("Análisis completado para la región seleccionada.")
            
            st.markdown("""
            **Resumen de Situación:**
            Se ha detectado una correlación crítica (R²=0.85) entre los tiempos de entrega >10 días y la caída del NPS en la zona Norte. Además, los 'Ghost SKUs' representan un riesgo financiero del 15% de la facturación total.

            **Plan de Acción Recomendado (Llama-3):**

            1.  **Protocolo de Saneamiento de Inventario (Inmediato):**
                * *Acción:* Auditar los SKUs `PROD-099` y `PROD-015`.
                * *Impacto:* Detener la pérdida de $8,600 USD mensuales detectada en la Fase 2.
                * *Decisión Ética:* Dar de baja temporalmente estos productos del e-commerce hasta corregir costos.

            2.  **Reestructuración Logística en Zona Norte:**
                * *Hallazgo:* Las demoras están concentradas en el operador logístico actual.
                * *Acción:* Migrar el 40% de los despachos a un proveedor express para reducir el promedio de entrega de 15 a 4 días.
                
            3.  **Campaña de Recuperación de Lealtad:**
                * *Acción:* Contactar a los clientes con NPS < 4 afectados por 'Ventas Ghost' ofreciendo un descuento del 20%.
            """)
