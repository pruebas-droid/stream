import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE LA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="TechLogistics | Senior Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Títulos y Estilos
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #1E3A8A; font-weight: bold;}
    .sub-header {font-size: 1.5rem; color: #4B5563;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">📊 TechLogistics: DSS & AI Strategy</p>', unsafe_allow_html=True)
st.markdown("---")

# -----------------------------------------------------------------------------
# 2. CARGA Y PROCESAMIENTO DE DATOS (ETL BÁSICO)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    # Cargar los archivos (Asegúrate que los nombres coinciden con tus archivos locales)
    try:
        df_inv = pd.read_csv("inventario_central_v2_limpio.csv")
        # El archivo de transacciones parece tener un nombre largo, ajústalo si es necesario
        df_trans = pd.read_csv("transacciones_logistica_final_unificado.xlsx - Sheet1.csv")
        df_feed = pd.read_csv("feedback_clientes_limpio.csv")
        return df_inv, df_trans, df_feed
    except FileNotFoundError as e:
        st.error(f"Error cargando archivos: {e}")
        return None, None, None

def create_master_table(inv, trans, feed):
    # Merge 1: Transacciones + Inventario (Left Join para mantener todas las ventas)
    # Asumimos que la llave común es SKU_ID (ajustar si los nombres varían ligeramente)
    df_merged = pd.merge(trans, inv, on="SKU_ID", how="left", suffixes=('_trx', '_inv'))
    
    # Merge 2: Resultado + Feedback (Left Join)
    # Asumimos que la llave común es Transaccion_ID
    df_final = pd.merge(df_merged, feed, on="Transaccion_ID", how="left")
    
    return df_final

# Ejecutar carga
df_inv, df_trans, df_feed = load_data()

if df_inv is not None:
    df_master = create_master_table(df_inv, df_trans, df_feed)
    st.sidebar.success("✅ Datos cargados y unificados correctamente")
    
    # Filtros Globales (Sidebar)
    st.sidebar.header("🔍 Filtros Globales")
    selected_city = st.sidebar.multiselect(
        "Filtrar por Ciudad", 
        options=df_master['Ciudad_Destino_norm'].unique(),
        default=df_master['Ciudad_Destino_norm'].unique()
    )
    
    # Filtrar el dataset maestro
    df_filtered = df_master[df_master['Ciudad_Destino_norm'].isin(selected_city)]

else:
    st.stop()

# -----------------------------------------------------------------------------
# 3. ESTRUCTURA DE PESTAÑAS
# -----------------------------------------------------------------------------
tab_audit, tab_eda, tab_ai = st.tabs([
    "📂 Auditoría & Calidad de Datos", 
    "📈 EDA: Análisis Exploratorio", 
    "🤖 Asistente Estratégico (Groq)"
])

# --- PESTAÑA 1: AUDITORÍA DE DATOS ---
with tab_audit:
    st.header("Auditoría de Limpieza")
    st.caption("Visualización de los datasets originales post-limpieza para validación.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Inventario")
        st.dataframe(df_inv.head(), use_container_width=True)
        st.info(f"Registros: {df_inv.shape[0]} | Cols: {df_inv.shape[1]}")
        
    with col2:
        st.subheader("Transacciones")
        st.dataframe(df_trans.head(), use_container_width=True)
        st.info(f"Registros: {df_trans.shape[0]} | Cols: {df_trans.shape[1]}")
        
    with col3:
        st.subheader("Feedback")
        st.dataframe(df_feed.head(), use_container_width=True)
        st.info(f"Registros: {df_feed.shape[0]} | Cols: {df_feed.shape[1]}")

    st.markdown("### Integridad del Master Table")
    st.write("Muestra del tablón unificado (Transacciones + Inventario + Feedback):")
    st.dataframe(df_master.head(3), use_container_width=True)

# --- PESTAÑA 2: EDA (UNIVARIADO & MULTIVARIADO) ---
with tab_eda:
    st.header("Análisis Exploratorio de Datos (EDA)")
    
    # Sub-sección: Univariado
    with st.expander("📊 Análisis Univariado (Distribuciones Individuales)", expanded=True):
        st.markdown("**Variables Cuantitativas (Ej. Precios, Tiempos)**")
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            # Placeholder para histograma
            st.metric("Total Ventas (USD)", f"${df_filtered['Precio_Venta_Final'].sum():,.2f}")
            fig_hist = px.histogram(df_filtered, x="Precio_Venta_Final", title="Distribución de Precios de Venta")
            st.plotly_chart(fig_hist, use_container_width=True)
            
        with col_u2:
            st.markdown("**Variables Cualitativas (Ej. Estado Envío, Rating)**")
            # Placeholder para conteo
            fig_bar = px.bar(df_filtered['Estado_Envio'].value_counts().reset_index(), 
                             x='Estado_Envio', y='count', title="Conteo por Estado de Envío")
            st.plotly_chart(fig_bar, use_container_width=True)

    # Sub-sección: Multivariado
    with st.expander("🔗 Análisis Multivariado (Correlaciones & Cruces)", expanded=True):
        st.markdown("Cruce de variables para responder preguntas de negocio.")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.subheader("Relación Precio vs. Costo")
            # Scatter Plot simple
            fig_scatter = px.scatter(
                df_filtered, 
                x="Costo_Unitario_USD", 
                y="Precio_Venta_Final", 
                color="Categoria",
                title="Dispersión: Costo vs. Precio Venta"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        with col_m2:
            st.subheader("Tiempo Entrega vs. Satisfacción (NPS)")
            # Boxplot o Scatter
            if 'Satisfaccion_NPS' in df_filtered.columns:
                fig_box = px.box(
                    df_filtered, 
                    x="Tiempo_Entrega_Real", 
                    y="Satisfaccion_NPS", 
                    title="Impacto del Tiempo en NPS"
                )
                st.plotly_chart(fig_box, use_container_width=True)
            else:
                st.warning("Columna NPS no encontrada en el merge.")

# --- PESTAÑA 3: IA & INSIGHTS ---
with tab_ai:
    st.header("🤖 Asistente Estratégico (Powered by Groq)")
    st.markdown("""
    Este módulo utiliza IA para interpretar los hallazgos del EDA y sugerir acciones correctivas.
    """)
    
    col_ai_input, col_ai_output = st.columns([1, 2])
    
    with col_ai_input:
        st.subheader("Consulta")
        user_query = st.text_area(
            "Escribe tu pregunta de negocio:",
            placeholder="Ej: ¿Por qué tenemos SKUs con stock alto y ventas bajas?",
            height=150
        )
        if st.button("Generar Insights 🚀"):
            st.toast("Conectando con Llama-3 en Groq...")
            # AQUI IRÁ LA LÓGICA DE LLAMADA A LA API
            st.session_state['ai_response'] = "🚧 [Simulación] La IA sugiere revisar los SKUs de la categoría 'Laptops' en la bodega Norte..."
            
    with col_ai_output:
        st.subheader("Respuesta Generativa")
        if 'ai_response' in st.session_state:
            st.info(st.session_state['ai_response'])
        else:
            st.markdown("*La respuesta de la IA aparecerá aquí...*")

# Footer
st.markdown("---")
st.caption("TechLogistics DSS v1.0 | Desarrollado con Streamlit & Python")
