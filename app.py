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

# Estilos personalizados
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #1E3A8A; font-weight: bold;}
    .sub-header {font-size: 1.5rem; color: #4B5563;}
    .upload-box {border: 2px dashed #4B5563; padding: 20px; border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">📊 TechLogistics: DSS & AI Strategy</p>', unsafe_allow_html=True)
st.markdown("---")

# -----------------------------------------------------------------------------
# 2. CARGA DE DATOS (MANUAL VIA SIDEBAR)
# -----------------------------------------------------------------------------
st.sidebar.header("📂 Configuración y Datos")
st.sidebar.markdown("Sube aquí los archivos limpios para iniciar el análisis.")

# Widgets de carga
up_inv = st.sidebar.file_uploader("1. Inventario (CSV)", type="csv")
up_trans = st.sidebar.file_uploader("2. Transacciones (CSV)", type="csv")
up_feed = st.sidebar.file_uploader("3. Feedback Clientes (CSV)", type="csv")

# Función de procesamiento (Cacheada para no re-ejecutar en cada click)
@st.cache_data
def process_and_merge(file_inv, file_trans, file_feed):
    # Leer CSVs desde los objetos subidos
    df_i = pd.read_csv(file_inv)
    df_t = pd.read_csv(file_trans)
    df_f = pd.read_csv(file_feed)
    
    # --- LÓGICA DE MERGE ---
    # Merge 1: Transacciones + Inventario
    # Aseguramos que SKU_ID sea string para evitar errores de tipo
    df_t['SKU_ID'] = df_t['SKU_ID'].astype(str)
    df_i['SKU_ID'] = df_i['SKU_ID'].astype(str)
    
    df_merged = pd.merge(df_t, df_i, on="SKU_ID", how="left", suffixes=('_trx', '_inv'))
    
    # Merge 2: Resultado + Feedback
    df_merged['Transaccion_ID'] = df_merged['Transaccion_ID'].astype(str)
    df_f['Transaccion_ID'] = df_f['Transaccion_ID'].astype(str)
    
    df_final = pd.merge(df_merged, df_f, on="Transaccion_ID", how="left")
    
    return df_i, df_t, df_f, df_final

# -----------------------------------------------------------------------------
# 3. LÓGICA PRINCIPAL (CONTROL DE FLUJO)
# -----------------------------------------------------------------------------

# Verificamos si TODO fue subido
if up_inv is not None and up_trans is not None and up_feed is not None:
    
    # Procesar datos
    try:
        df_inv, df_trans, df_feed, df_master = process_and_merge(up_inv, up_trans, up_feed)
        st.sidebar.success("✅ Datos procesados exitosamente!")
        
        # Filtros Globales que aparecen SOLO cuando hay datos
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔍 Filtros de Visualización")
        
        if 'Ciudad_Destino_norm' in df_master.columns:
            ciudades = df_master['Ciudad_Destino_norm'].unique()
            selected_city = st.sidebar.multiselect("Filtrar por Ciudad", ciudades, default=ciudades)
            df_filtered = df_master[df_master['Ciudad_Destino_norm'].isin(selected_city)]
        else:
            df_filtered = df_master # Fallback si no existe la columna
            
    except Exception as e:
        st.error(f"Error procesando los archivos. Verifica que sean los CSV correctos.\nDetalle: {e}")
        st.stop()

    # -------------------------------------------------------------------------
    # 4. ESTRUCTURA DE PESTAÑAS (Solo visible si hay datos)
    # -------------------------------------------------------------------------
    tab_audit, tab_eda, tab_ai = st.tabs([
        "📂 Auditoría & Calidad", 
        "📈 EDA: Análisis Exploratorio", 
        "🤖 Asistente IA"
    ])

    # --- TAB 1: AUDITORÍA ---
    with tab_audit:
        st.header("Vista Previa de Datos")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Inventario")
            st.dataframe(df_inv.head(5), use_container_width=True)
            st.caption(f"{df_inv.shape[0]} filas | {df_inv.shape[1]} cols")
        with col2:
            st.subheader("Transacciones")
            st.dataframe(df_trans.head(5), use_container_width=True)
            st.caption(f"{df_trans.shape[0]} filas | {df_trans.shape[1]} cols")
        with col3:
            st.subheader("Feedback")
            st.dataframe(df_feed.head(5), use_container_width=True)
            st.caption(f"{df_feed.shape[0]} filas | {df_feed.shape[1]} cols")
            
        st.markdown("### Master Table (Unificado)")
        st.dataframe(df_master.head(), use_container_width=True)

    # --- TAB 2: EDA ---
    with tab_eda:
        st.header("Análisis Exploratorio")
        
        # Métricas Top (KPIs rápidos)
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Ventas Totales", f"${df_filtered['Precio_Venta_Final'].sum():,.0f}")
        kpi2.metric("Transacciones", f"{df_filtered.shape[0]:,}")
        
        # Calcular margen promedio si existen las columnas
        if 'Costo_Unitario_USD' in df_filtered.columns:
            margen_prom = (df_filtered['Precio_Venta_Final'] - df_filtered['Costo_Unitario_USD']).mean()
            kpi3.metric("Margen Promedio (aprox)", f"${margen_prom:,.2f}")
        
        st.markdown("---")
        
        # Gráficas
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.subheader("Distribución de Precios")
            fig_hist = px.histogram(df_filtered, x="Precio_Venta_Final", nbins=30, 
                                    title="Histograma de Ventas")
            st.plotly_chart(fig_hist, use_container_width=True)
            
        with col_g2:
            if 'Categoria' in df_filtered.columns:
                st.subheader("Ventas por Categoría")
                fig_bar = px.bar(df_filtered.groupby('Categoria')['Precio_Venta_Final'].sum().reset_index(),
                                 x='Categoria', y='Precio_Venta_Final',
                                 title="Total Vendido por Categoría")
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Columna 'Categoria' no encontrada para graficar.")

    # --- TAB 3: IA ---
    with tab_ai:
        st.header("🤖 Insights Generativos")
        st.info("Sube tus credenciales de Groq en el sidebar o config (Pendiente de implementación)")
        user_q = st.text_input("Pregunta a tus datos:")
        if st.button("Consultar"):
            st.write(f"Simulando respuesta para: '{user_q}'...")
            st.success("La IA sugiere revisar el inventario en la bodega Norte.")

else:
    # -------------------------------------------------------------------------
    # PANTALLA DE BIENVENIDA (ESTADO INICIAL)
    # -------------------------------------------------------------------------
    st.info("👋 ¡Bienvenido al DSS de TechLogistics!")
    st.markdown("""
        Para comenzar, por favor utiliza el menú de la izquierda (**Sidebar**) para subir tus tres archivos CSV:
        
        1.  `inventario_central_*.csv`
        2.  `transacciones_logistica_*.csv`
        3.  `feedback_clientes_*.csv`
        
        *El sistema unificará los datos automáticamente una vez cargados.*
    """)
    # Imagen opcional de placeholder o instrucción visual
    st.warning("⚠️ Esperando archivos...")
