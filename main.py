import streamlit as st
import pandas as pd
import json
import re
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Congreso de los Diputados - Portal de Transparencia",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- HELPER FUNCTIONS ---
def parse_json_field(field_value):
    """Safely parse JSON string fields."""
    if pd.isna(field_value) or field_value in ["", "[]", None]:
        return []
    try:
        data = json.loads(field_value)
        return data if isinstance(data, list) else [data]
    except (json.JSONDecodeError, TypeError):
        return []

def parse_currency_value(value):
    """Convert currency strings to float."""
    if value is None or pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    s_value = str(value).strip().replace('€', '').replace(' ', '').replace('.', '').replace(',', '.')
    try:
        return float(s_value)
    except (ValueError, TypeError):
        return 0.0

def format_currency(value):
    """Format number as currency."""
    if pd.isna(value) or not isinstance(value, (int, float)):
        return "No declarado"
    return f"{value:,.2f} €"

# --- DATA LOADING ---
@st.cache_data
def load_data():
    """Load and preprocess the dataset."""
    try:
        df = pd.read_csv('deputies_full_dataset.csv')
        
        # Check if dataframe is empty
        if df.empty:
            st.error("❌ El archivo de datos está vacío")
            return pd.DataFrame()
        
        # Fix: Extract returns a DataFrame, select first column with [0]
        if 'source_file' in df.columns:
            df['declaration_date'] = pd.to_datetime(
                df['source_file'].str.extract(r'(\d{8})\.json$')[0], 
                errors='coerce'
            )
            df = df.sort_values('declaration_date', ascending=False).drop_duplicates('deputy_id', keep='first')
        
        # Ensure name column exists and fill NaN values
        if 'informacion_personal_nombre_y_apellidos' in df.columns:
            df['informacion_personal_nombre_y_apellidos'] = df['informacion_personal_nombre_y_apellidos'].fillna("Nombre no disponible")
            df = df.sort_values('informacion_personal_nombre_y_apellidos')
        
        return df
        
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo 'deputies_full_dataset.csv'")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error al cargar los datos: {str(e)}")
        return pd.DataFrame()

# --- CSS STYLING ---
def inject_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* Reset and base */
        .stApp {
            background: linear-gradient(135deg, #1a1a2e 0%, #0f0f23 100%);
            color: #e0e0e0;
        }
        
        /* Headers */
        .main-header {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .main-title {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            padding: 0;
        }
        
        .main-subtitle {
            color: rgba(255, 255, 255, 0.6);
            font-size: 1.1rem;
            margin-top: 10px;
        }
        
        /* Cards */
        .info-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            transition: all 0.3s ease;
        }
        
        .info-card:hover {
            background: rgba(255, 255, 255, 0.08);
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }
        
        /* Metrics */
        [data-testid="metric-container"] {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        
        [data-testid="stMetricValue"] {
            color: #667eea !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: rgba(255, 255, 255, 0.6) !important;
            font-weight: 500 !important;
        }
        
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: rgba(20, 20, 40, 0.95);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 5px;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: rgba(255, 255, 255, 0.7);
            font-weight: 600;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: rgba(102, 126, 234, 0.2);
            color: white;
        }
        
        /* Info rows */
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 12px;
            margin: 8px 0;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            border-left: 3px solid #667eea;
        }
        
        .info-label {
            color: rgba(255, 255, 255, 0.6);
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .info-value {
            color: #e0e0e0;
            font-weight: 600;
        }
        
        /* Expanders */
        .streamlit-expanderHeader {
            background: rgba(255, 255, 255, 0.05) !important;
            border-radius: 10px !important;
            color: white !important;
        }
        
        /* Social buttons */
        .social-link {
            display: inline-block;
            padding: 8px 16px;
            margin: 5px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white !important;
            text-decoration: none !important;
            border-radius: 20px;
            font-weight: 600;
            transition: transform 0.3s ease;
        }
        
        .social-link:hover {
            transform: scale(1.05);
        }
    </style>
    """, unsafe_allow_html=True)

# --- MAIN APP ---
def main():
    # Inject CSS
    inject_css()
    
    # Title
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">⚡ Portal de Transparencia</h1>
            <p class="main-subtitle">Congreso de los Diputados de España</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    # Check if data loaded successfully
    if df.empty:
        st.warning("⚠️ No hay datos disponibles para mostrar")
        st.info("Por favor, asegúrese de que el archivo 'deputies_full_dataset.csv' está en el directorio correcto")
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🏛️ Panel de Control")
        st.markdown("---")
        
        # Search
        search = st.text_input("🔍 Buscar diputado", "")
        
        # Filter by constituency
        if 'informacion_personal_circunscripcion' in df.columns:
            constituencies = ["Todas"] + sorted(df['informacion_personal_circunscripcion'].dropna().unique().tolist())
            selected_constituency = st.selectbox("📍 Circunscripción", constituencies)
        else:
            selected_constituency = "Todas"
        
        # Apply filters
        filtered_df = df.copy()
        
        if search and 'informacion_personal_nombre_y_apellidos' in df.columns:
            filtered_df = filtered_df[
                filtered_df['informacion_personal_nombre_y_apellidos'].str.contains(
                    search, case=False, na=False
                )
            ]
        
        if selected_constituency != "Todas" and 'informacion_personal_circunscripcion' in df.columns:
            filtered_df = filtered_df[
                filtered_df['informacion_personal_circunscripcion'] == selected_constituency
            ]
        
        if filtered_df.empty:
            st.error("No se encontraron resultados")
            return
        
        # Deputy selector
        st.markdown("---")
        
        if 'informacion_personal_nombre_y_apellidos' in filtered_df.columns:
            deputy_names = filtered_df['informacion_personal_nombre_y_apellidos'].tolist()
            selected_deputy = st.selectbox("👤 Seleccionar Diputado/a", deputy_names)
        else:
            st.error("No se encontró la columna de nombres")
            return
        
        # Statistics
        st.markdown("---")
        st.markdown("### 📊 Estadísticas")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total", len(df))
        with col2:
            st.metric("Filtrados", len(filtered_df))
    
    # Main content
    if selected_deputy:
        deputy_data = filtered_df[
            filtered_df['informacion_personal_nombre_y_apellidos'] == selected_deputy
        ].iloc[0]
        
        # Header
        st.markdown(f"""
            <div class="info-card" style="text-align: center;">
                <h1 style="color: #667eea; font-size: 2.5rem; margin: 0;">
                    {deputy_data.get('informacion_personal_nombre_y_apellidos', 'Nombre no disponible')}
                </h1>
                <p style="color: rgba(255,255,255,0.6); font-size: 1.2rem; margin-top: 10px;">
                    {deputy_data.get('informacion_personal_cargo', 'Diputado/a')} - 
                    {deputy_data.get('informacion_personal_circunscripcion', 'España')}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Social media links
        social_links = []
        if pd.notna(deputy_data.get('facebook')):
            social_links.append(f'<a href="{deputy_data.get("facebook")}" target="_blank" class="social-link">📘 Facebook</a>')
        if pd.notna(deputy_data.get('twitter')):
            social_links.append(f'<a href="{deputy_data.get("twitter")}" target="_blank" class="social-link">🐦 Twitter</a>')
        if pd.notna(deputy_data.get('instagram')):
            social_links.append(f'<a href="{deputy_data.get("instagram")}" target="_blank" class="social-link">📸 Instagram</a>')
        if pd.notna(deputy_data.get('website')):
            social_links.append(f'<a href="{deputy_data.get("website")}" target="_blank" class="social-link">🌐 Web</a>')
        
        if social_links:
            st.markdown(f'<div style="text-align: center; margin: 20px 0;">{"".join(social_links)}</div>', unsafe_allow_html=True)
        
        # Calculate metrics
        total_rentas = sum(
            parse_currency_value(r.get('euros')) 
            for r in parse_json_field(deputy_data.get('rentas_percibidas_percepciones_salariales', []))
        )
        
        otras_rentas = sum([
            sum(parse_currency_value(r.get('euros')) for r in parse_json_field(deputy_data.get('rentas_percibidas_dividendos_y_participaciones', []))),
            sum(parse_currency_value(r.get('euros')) for r in parse_json_field(deputy_data.get('rentas_percibidas_intereses_financieros', []))),
            sum(parse_currency_value(r.get('euros')) for r in parse_json_field(deputy_data.get('rentas_percibidas_otras_rentas', [])))
        ])
        
        total_deudas = sum(
            parse_currency_value(d.get('saldo_pendiente')) 
            for d in parse_json_field(deputy_data.get('deudas_y_obligaciones', []))
        )
        
        irpf_pagado = parse_currency_value(deputy_data.get('irpf_cantidad_pagada'))
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Ingresos Salariales", format_currency(total_rentas))
        with col2:
            st.metric("📈 Otras Rentas", format_currency(otras_rentas))
        with col3:
            st.metric("💳 Deuda Pendiente", format_currency(total_deudas))
        with col4:
            st.metric("🏛️ IRPF Pagado", format_currency(irpf_pagado))
        
        # Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "👤 Personal",
            "💰 Rentas",
            "🏠 Patrimonio",
            "📊 Financiero",
            "📋 Deudas"
        ])
        
        with tab1:
            st.markdown("### Información Personal")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                    <div class="info-card">
                        <div class="info-row">
                            <span class="info-label">Estado Civil</span>
                            <span class="info-value">{deputy_data.get('informacion_personal_estado_civil', 'No declarado')}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Fecha de Elección</span>
                            <span class="info-value">{deputy_data.get('informacion_personal_fecha_eleccion', 'No declarado')}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div class="info-card">
                        <div class="info-row">
                            <span class="info-label">Régimen Económico</span>
                            <span class="info-value">{deputy_data.get('informacion_personal_regimen_economico_matrimonial', 'No aplica')}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Fecha Credencial</span>
                            <span class="info-value">{deputy_data.get('informacion_personal_fecha_presentacion_credencial', 'No declarado')}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        with tab2:
            st.markdown("### Declaración de Rentas 2022")
            
            # Percepciones salariales
            salariales = parse_json_field(deputy_data.get('rentas_percibidas_percepciones_salariales'))
            if salariales:
                with st.expander("💼 Percepciones Salariales", expanded=True):
                    for item in salariales:
                        concepto = item.get('concepto', 'Sin descripción')
                        euros = format_currency(parse_currency_value(item.get('euros')))
                        st.markdown(f"- **{concepto}**: {euros}")
            
            # Dividendos
            dividendos = parse_json_field(deputy_data.get('rentas_percibidas_dividendos_y_participaciones'))
            if dividendos:
                with st.expander("📈 Dividendos y Participaciones"):
                    for item in dividendos:
                        concepto = item.get('concepto', 'Sin descripción')
                        euros = format_currency(parse_currency_value(item.get('euros')))
                        st.markdown(f"- **{concepto}**: {euros}")
        
        with tab3:
            st.markdown("### Bienes Patrimoniales")
            
            # Inmuebles urbanos
            urbanos = parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_urbanos'))
            if urbanos:
                with st.expander("🏢 Inmuebles Urbanos", expanded=True):
                    for item in urbanos:
                        st.markdown(f"""
                            <div class="info-card">
                                <strong>{item.get('clase_y_caracteristicas', 'Inmueble')}</strong><br>
                                📍 {item.get('situacion', 'Ubicación no especificada')}<br>
                                📋 {item.get('titulo_adquisicion', 'No especificado')}<br>
                                📊 {item.get('porcentaje_sobre_el_bien', '100')}% de propiedad
                            </div>
                        """, unsafe_allow_html=True)
            
            # Vehículos
            vehiculos = parse_json_field(deputy_data.get('vehiculos'))
            if vehiculos:
                with st.expander("🚗 Vehículos"):
                    for v in vehiculos:
                        st.markdown(f"- **{v.get('marca_y_modelo', 'No especificado')}** - Adquirido: {v.get('fecha_adquisicion', 'N/A')}")
        
        with tab4:
            st.markdown("### Activos Financieros")
            
            # Cuentas bancarias
            cuentas = parse_json_field(deputy_data.get('depositos_y_cuentas_cuentas'))
            if cuentas:
                with st.expander("🏦 Cuentas y Depósitos", expanded=True):
                    for cuenta in cuentas:
                        desc = cuenta.get('descripcion', cuenta.get('tipo', 'Cuenta'))
                        saldo = format_currency(parse_currency_value(cuenta.get('saldo')))
                        st.markdown(f"- **{desc}**: {saldo}")
            
            # Acciones
            acciones = parse_json_field(deputy_data.get('otros_bienes_y_derechos_acciones_y_participaciones'))
            if acciones:
                with st.expander("📈 Acciones y Participaciones"):
                    for item in acciones:
                        desc = item.get('descripcion', 'N/A')
                        valor = format_currency(parse_currency_value(item.get('valor')))
                        st.markdown(f"- **{desc}**: {valor}")
        
        with tab5:
            st.markdown("### Deudas y Obligaciones")
            
            deudas = parse_json_field(deputy_data.get('deudas_y_obligaciones'))
            if deudas:
                for deuda in deudas:
                    desc = deuda.get('descripcion', deuda.get('prestamo', 'Deuda'))
                    st.markdown(f"""
                        <div class="info-card">
                            <strong>{desc}</strong><br>
                            📅 Fecha: {deuda.get('fecha_concesion', 'N/A')}<br>
                            💰 Importe original: {format_currency(parse_currency_value(deuda.get('importe_concedido')))}<br>
                            💳 Saldo pendiente: {format_currency(parse_currency_value(deuda.get('saldo_pendiente')))}
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No hay deudas declaradas")
            
            # Observaciones
            if pd.notna(deputy_data.get('observaciones')) and deputy_data.get('observaciones'):
                st.markdown("### 📝 Observaciones")
                st.markdown(f"""
                    <div class="info-card">
                        {deputy_data.get('observaciones')}
                    </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
