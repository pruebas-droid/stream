import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="TechLogistics | Senior Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- 2. FUNCIÓN DE DATOS MOCK (PARA QUE FUNCIONE SIN CSV) ---
# Esto permite ver la app funcionando aunque no tengas los archivos reales aún.
@st.cache_data
def load_mock_data():
    # Mock Inventario
    df_inv = pd.DataFrame({
        'SKU': [f'PROD-{i}' for i in range(100)],
        'Costo': np.random.uniform(10, 100, 100),
        'Stock': np.random.randint(-10, 500, 100) # Algunos negativos para simular error
    })
    
    # Mock Transacciones (con SKUs que no existen en inventario para el reto "Ghost SKU")
    df_trans = pd.DataFrame({
        'ID_Venta': range(1000),
        'SKU': [f'PROD-{np.random.randint(0, 110)}' for _ in range(1000)], # SKUs 100-110 son fantasmas
        'Precio_Venta': np.random.uniform(20, 150, 1000),
        'Dias_Entrega': np.concatenate([np.random.normal(5, 2, 950), [999]*50]) # Outliers de 999
    })
    
    # Mock Feedback
    df_feed = pd.DataFrame({
        'ID_Cliente': range(500),
        'NPS': np.random.randint(0, 11, 500),
        'Region': np.random.choice(['Norte', 'Sur', 'Centro', 'Occidente'], 500)
    })
    
    return df_inv, df_trans, df_feed

# --- 3. SIDEBAR (CONTROLES) ---
with st.sidebar:
    st.title("🔧 Panel de Control")
    st.info("💡 Modo Demostración: Usando datos generados automáticamente.")
    
    # Filtros simulados
    region = st.multiselect("Región", ['Norte', 'Sur', 'Centro', 'Occidente'], default=['Norte'])
    
    st.divider()
    st.caption("TechLogistics S.A.S. - [cite_start]Módulo de Auditoría [cite: 7]")

# Cargar datos (Mock o Reales)
df_inv, df_trans, df_feed = load_mock_data()

# --- 4. LAYOUT PRINCIPAL ---
st.title("📊 TechLogistics: Data Strategy Dashboard")
st.markdown("""
> [cite_start]**Resumen Ejecutivo:** Dashboard diseñado para auditar la calidad de datos y resolver la crisis de lealtad y margen. [cite: 9]
""")

# Definir Tabs
tab1, tab2, tab3 = st.tabs(["🏥 Fase 1: Auditoría", "📈 Fase 2: Insights", "🤖 Fase 3: IA Consultant"])

# ==============================================================================
# [cite_start]TAB 1: AUDITORÍA (Interactiva) [cite: 18]
# ==============================================================================
with tab1:
    st.header("Auditoría de Calidad de Datos")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("⚙️ Parámetros")
        clean_mode = st.radio("Modo de Limpieza", ["Estándar", "Agresiva (Eliminar todo)"])
        outlier_threshold = st.slider("Umbral de Outliers (Días)", 10, 100, 30, help="Días máximos permitidos antes de considerar error")
        
        # Botón con estado
        if 'cleaned' not in st.session_state:
            st.session_state.cleaned = False
            
        if st.button("🔄 Ejecutar Limpieza"):
            with st.spinner("Limpiando duplicados y outliers..."):
                time.sleep(1) # Simular proceso
                st.session_state.cleaned = True
                
    with col2:
        st.subheader("Diagnóstico de Salud (Health Score)")
        
        # Métricas dinámicas basadas en si se limpió o no
        c1, c2, c3 = st.columns(3)
        
        if st.session_state.cleaned:
            c1.metric("Registros Totales", "2,450", "-50 (Eliminados)", delta_color="inverse")
            c2.metric("Outliers (999 días)", "0", "-50 detectados", delta_color="inverse")
            c3.metric("Health Score", "98/100", "+35 pts")
            st.success("✅ Datos limpios y listos para análisis.")
            
            # Gráfico de comparación Antes/Después
            clean_data = pd.DataFrame({'Estado': ['Sucio', 'Limpio'], 'Calidad': [65, 98]})
            fig_health = px.bar(clean_data, x='Estado', y='Calidad', color='Estado', range_y=[0,100])
            st.plotly_chart(fig_health, use_container_width=True)
            
        else:
            c1.metric("Registros Totales", "2,500", "Datos Crudos")
            c2.metric("Outliers (999 días)", "50", "Critico", delta_color="inverse")
            c3.metric("Health Score", "65/100", "Bajo Riesgo", delta_color="inverse")
            st.warning("⚠️ Se detectaron inconsistencias graves. Ejecute la limpieza.")

# ==============================================================================
# [cite_start]TAB 2: INSIGHTS (Gráficos Reales) [cite: 33]
# ==============================================================================
with tab2:
    st.header("Tablero Estratégico")
    
    # Fila 1: Finanzas y Logística
    row1_1, row1_2 = st.columns(2)
    
    with row1_1:
        st.markdown("#### 💰 Fuga de Capital (Márgen Negativo)")
        # Crear gráfico dummy de pérdidas
        loss_data = pd.DataFrame({'SKU': ['Laptop X', 'Mouse Y', 'Screen Z'], 'Pérdida': [-5000, -2000, -1500]})
        fig_loss = px.bar(loss_data, x='SKU', y='Pérdida', color='Pérdida', color_continuous_scale='reds')
        st.plotly_chart(fig_loss, use_container_width=True)
        [cite_start]st.caption("Estos SKUs se venden por debajo del costo [cite: 37]")

    with row1_2:
        st.markdown("#### 🚚 Tiempos de Entrega vs Satisfacción")
        # Crear gráfico dummy de dispersión
        fig_scatter = px.scatter(
            x=np.random.randint(1, 30, 50), 
            y=np.random.randint(1, 10, 50),
            labels={'x': 'Días Entrega', 'y': 'NPS (Satisfacción)'},
            color_discrete_sequence=['#FF4B4B']
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        [cite_start]st.caption("Correlación clara: Mayor tiempo implica menor NPS [cite: 39]")

# ==============================================================================
# [cite_start]TAB 3: IA (Simulación) [cite: 31]
# ==============================================================================
with tab3:
    st.header("🤖 Consultor Virtual (Groq)")
    
    query = st.text_input("Pregunta a la IA:", placeholder="¿Por qué está bajando el margen en el Norte?")
    
    if st.button("Generar Respuesta"):
        st.markdown("### Análisis Generado:")
        st.markdown("""
        **Estrategia Recomendada:**
        1. **Bloqueo de SKUs:** Se han identificado 3 productos ('Laptop X') con margen negativo del 15%. Se recomienda detener su venta online inmediatamente.
        2. **Alerta Logística:** La región Norte tiene un promedio de entrega de 12 días, muy superior al KPI de 3 días.
        3. **Acción:** Renegociar contrato con proveedor logístico local.
        """)
