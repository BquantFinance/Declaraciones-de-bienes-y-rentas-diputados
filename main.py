import streamlit as st
import pandas as pd
import json
import re
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Congreso de los Diputados - Portal de Transparencia",
    page_icon="🏛️",
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
    if value > 1000000:
        return f"💎 {value:,.2f} €"
    elif value > 100000:
        return f"⭐ {value:,.2f} €"
    else:
        return f"{value:,.2f} €"

# --- DATA LOADING ---
@st.cache_data
def load_data():
    """Load and preprocess the dataset."""
    try:
        df = pd.read_csv('deputies_full_dataset.csv')
        
        if df.empty:
            return pd.DataFrame()
        
        if 'source_file' in df.columns:
            df['declaration_date'] = pd.to_datetime(
                df['source_file'].str.extract(r'(\d{8})\.json$')[0], 
                errors='coerce'
            )
            df = df.sort_values('declaration_date', ascending=False).drop_duplicates('deputy_id', keep='first')
        
        if 'informacion_personal_nombre_y_apellidos' in df.columns:
            df['informacion_personal_nombre_y_apellidos'] = df['informacion_personal_nombre_y_apellidos'].fillna("Nombre no disponible")
            df = df.sort_values('informacion_personal_nombre_y_apellidos')
        
        return df
        
    except FileNotFoundError:
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return pd.DataFrame()

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Dark theme base */
    .stApp {
        background: linear-gradient(180deg, #0f0f23 0%, #1a1a3e 100%);
    }
    
    /* Custom header */
    .main-header {
        background: linear-gradient(135deg, rgba(88, 101, 242, 0.1), rgba(214, 51, 132, 0.1));
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #5865f2, #d63384);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .main-subtitle {
        color: rgba(255, 255, 255, 0.7);
        font-size: 1.2rem;
        margin-top: 0.5rem;
    }
    
    /* Card styles */
    .custom-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .deputy-name-card {
        background: linear-gradient(135deg, rgba(88, 101, 242, 0.15), rgba(214, 51, 132, 0.15));
        border: 1px solid rgba(88, 101, 242, 0.3);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
    }
    
    .deputy-name {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
    }
    
    .deputy-info {
        color: rgba(255, 255, 255, 0.7);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Social buttons */
    .social-button {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        margin: 0.5rem;
        border-radius: 25px;
        text-decoration: none;
        color: white;
        font-weight: 600;
        transition: transform 0.2s;
    }
    
    .social-button:hover {
        transform: translateY(-2px);
    }
    
    .social-facebook { background: linear-gradient(135deg, #1877f2, #0c63d4); }
    .social-twitter { background: linear-gradient(135deg, #1da1f2, #0c85d0); }
    .social-instagram { background: linear-gradient(135deg, #e1306c, #f77737); }
    .social-website { background: linear-gradient(135deg, #5865f2, #3f51b5); }
    
    /* Info rows */
    .info-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        margin: 0.5rem 0;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
        border-left: 3px solid #5865f2;
    }
    
    .info-label {
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .info-value {
        color: #ffffff;
        font-size: 1rem;
        font-weight: 600;
    }
    
    /* Metrics override */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        border-radius: 15px;
    }
    
    [data-testid="stMetricValue"] {
        color: #5865f2;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(255, 255, 255, 0.05);
        padding: 4px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: rgba(255, 255, 255, 0.7);
        font-weight: 600;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: rgba(88, 101, 242, 0.2);
        color: white;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 15, 35, 0.95);
    }
    
    /* Text color fixes */
    .stMarkdown, .stText {
        color: rgba(255, 255, 255, 0.9);
    }
</style>
""", unsafe_allow_html=True)

# --- MAIN APP ---
def main():
    # Load data
    df = load_data()
    
    # Header
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">🏛️ Portal de Transparencia</h1>
            <p class="main-subtitle">Congreso de los Diputados de España</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Check if data is loaded
    if df.empty:
        st.error("⚠️ No se pudo cargar el archivo de datos 'deputies_full_dataset.csv'")
        st.info("Por favor, asegúrese de que el archivo existe en el directorio del proyecto.")
        
        # Show sample structure
        st.markdown("### 📋 Estructura esperada del archivo CSV:")
        expected_cols = [
            "deputy_id",
            "informacion_personal_nombre_y_apellidos",
            "informacion_personal_circunscripcion",
            "informacion_personal_cargo",
            "informacion_personal_estado_civil",
            "informacion_personal_fecha_eleccion"
        ]
        st.code("\n".join(expected_cols))
        return
    
    # Show data info
    st.success(f"✅ Datos cargados correctamente: {len(df)} diputados encontrados")
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎯 Panel de Control")
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
        
        # Deputy header
        st.markdown(f"""
            <div class="deputy-name-card">
                <h1 class="deputy-name">{deputy_data.get('informacion_personal_nombre_y_apellidos', 'Nombre no disponible')}</h1>
                <p class="deputy-info">
                    {deputy_data.get('informacion_personal_cargo', 'Diputado/a')} • 
                    {deputy_data.get('informacion_personal_circunscripcion', 'España')}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Social media
        social_html = ""
        if pd.notna(deputy_data.get('facebook')):
            social_html += f'<a href="{deputy_data.get("facebook")}" target="_blank" class="social-button social-facebook">📘 Facebook</a>'
        if pd.notna(deputy_data.get('twitter')):
            social_html += f'<a href="{deputy_data.get("twitter")}" target="_blank" class="social-button social-twitter">🐦 Twitter</a>'
        if pd.notna(deputy_data.get('instagram')):
            social_html += f'<a href="{deputy_data.get("instagram")}" target="_blank" class="social-button social-instagram">📸 Instagram</a>'
        if pd.notna(deputy_data.get('website')):
            social_html += f'<a href="{deputy_data.get("website")}" target="_blank" class="social-button social-website">🌐 Web</a>'
        
        if social_html:
            st.markdown(f'<div style="text-align: center; margin: 2rem 0;">{social_html}</div>', unsafe_allow_html=True)
        
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
        st.markdown("## 💰 Resumen Financiero")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💵 Ingresos Salariales", format_currency(total_rentas))
        with col2:
            st.metric("📈 Otras Rentas", format_currency(otras_rentas))
        with col3:
            st.metric("💳 Deuda Pendiente", format_currency(total_deudas))
        with col4:
            st.metric("🏛️ IRPF Pagado", format_currency(irpf_pagado))
        
        st.markdown("---")
        
        # Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "👤 Personal",
            "💰 Rentas",
            "🏠 Patrimonio",
            "📊 Financiero",
            "📋 Deudas"
        ])
        
        with tab1:
            st.markdown("### 📝 Información Personal")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="custom-card">', unsafe_allow_html=True)
                st.markdown(f"""
                    <div class="info-row">
                        <span class="info-label">Estado Civil</span>
                        <span class="info-value">{deputy_data.get('informacion_personal_estado_civil', 'No declarado')}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Fecha de Elección</span>
                        <span class="info-value">{deputy_data.get('informacion_personal_fecha_eleccion', 'No declarado')}</span>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="custom-card">', unsafe_allow_html=True)
                st.markdown(f"""
                    <div class="info-row">
                        <span class="info-label">Régimen Económico</span>
                        <span class="info-value">{deputy_data.get('informacion_personal_regimen_economico_matrimonial', 'No aplica')}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Fecha Credencial</span>
                        <span class="info-value">{deputy_data.get('informacion_personal_fecha_presentacion_credencial', 'No declarado')}</span>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown("### 💵 Declaración de Rentas 2022")
            
            # Salariales
            salariales = parse_json_field(deputy_data.get('rentas_percibidas_percepciones_salariales'))
            if salariales:
                with st.expander(f"💼 Percepciones Salariales ({len(salariales)} registros)", expanded=True):
                    for item in salariales:
                        concepto = item.get('concepto', 'Sin descripción')
                        euros = format_currency(parse_currency_value(item.get('euros')))
                        st.markdown(f"**{concepto}**: {euros}")
            
            # Dividendos
            dividendos = parse_json_field(deputy_data.get('rentas_percibidas_dividendos_y_participaciones'))
            if dividendos:
                with st.expander(f"📈 Dividendos y Participaciones ({len(dividendos)} registros)"):
                    for item in dividendos:
                        concepto = item.get('concepto', 'Sin descripción')
                        euros = format_currency(parse_currency_value(item.get('euros')))
                        st.markdown(f"**{concepto}**: {euros}")
            
            # Intereses
            intereses = parse_json_field(deputy_data.get('rentas_percibidas_intereses_financieros'))
            if intereses:
                with st.expander(f"🏦 Intereses Financieros ({len(intereses)} registros)"):
                    for item in intereses:
                        concepto = item.get('concepto', 'Sin descripción')
                        euros = format_currency(parse_currency_value(item.get('euros')))
                        st.markdown(f"**{concepto}**: {euros}")
            
            # Otras rentas
            otras = parse_json_field(deputy_data.get('rentas_percibidas_otras_rentas'))
            if otras:
                with st.expander(f"📑 Otras Rentas ({len(otras)} registros)"):
                    for item in otras:
                        concepto = item.get('concepto', 'Sin descripción')
                        euros = format_currency(parse_currency_value(item.get('euros')))
                        st.markdown(f"**{concepto}**: {euros}")
        
        with tab3:
            st.markdown("### 🏘️ Bienes Patrimoniales")
            
            # Inmuebles urbanos
            urbanos = parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_urbanos'))
            if urbanos:
                st.markdown("#### 🏢 Inmuebles Urbanos")
                for idx, item in enumerate(urbanos, 1):
                    with st.expander(f"Propiedad #{idx}"):
                        st.markdown(f"📍 **Ubicación**: {item.get('situacion', 'No especificado')}")
                        st.markdown(f"🏠 **Tipo**: {item.get('clase_y_caracteristicas', 'No especificado')}")
                        st.markdown(f"📄 **Título**: {item.get('titulo_adquisicion', 'No especificado')}")
                        st.markdown(f"📊 **Porcentaje**: {item.get('porcentaje_sobre_el_bien', '100')}%")
            
            # Rústicos
            rusticos = parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_rusticos'))
            if rusticos:
                st.markdown("#### 🌳 Inmuebles Rústicos")
                for idx, item in enumerate(rusticos, 1):
                    with st.expander(f"Propiedad Rústica #{idx}"):
                        st.markdown(f"📍 **Ubicación**: {item.get('situacion', 'No especificado')}")
                        st.markdown(f"🌾 **Tipo**: {item.get('clase_y_caracteristicas', 'No especificado')}")
            
            # Vehículos
            vehiculos = parse_json_field(deputy_data.get('vehiculos'))
            if vehiculos:
                st.markdown("#### 🚗 Vehículos")
                for v in vehiculos:
                    st.markdown(f"🚙 **{v.get('marca_y_modelo', 'No especificado')}** - Adquirido: {v.get('fecha_adquisicion', 'N/A')}")
        
        with tab4:
            st.markdown("### 💼 Activos Financieros")
            
            # Cuentas
            cuentas = parse_json_field(deputy_data.get('depositos_y_cuentas_cuentas'))
            if cuentas:
                st.markdown("#### 🏦 Cuentas y Depósitos")
                total_cuentas = sum(parse_currency_value(c.get('saldo')) for c in cuentas)
                st.info(f"💰 **Total en cuentas**: {format_currency(total_cuentas)}")
                
                for cuenta in cuentas:
                    tipo = cuenta.get('descripcion', cuenta.get('tipo', 'Cuenta'))
                    saldo = format_currency(parse_currency_value(cuenta.get('saldo')))
                    st.markdown(f"• **{tipo}**: {saldo}")
            
            # Acciones
            acciones = parse_json_field(deputy_data.get('otros_bienes_y_derechos_acciones_y_participaciones'))
            if acciones:
                st.markdown("#### 📈 Acciones y Participaciones")
                for item in acciones:
                    desc = item.get('descripcion', 'N/A')
                    valor = format_currency(parse_currency_value(item.get('valor')))
                    st.markdown(f"• **{desc}**: {valor}")
            
            # Sociedades
            sociedades = parse_json_field(deputy_data.get('bienes_patrimoniales_bienes_sociedades_no_cotizadas'))
            if sociedades:
                st.markdown("#### 🏢 Sociedades no cotizadas")
                for item in sociedades:
                    st.markdown(f"• **{item.get('clase_y_caracteristicas', 'N/A')}** - {item.get('situacion', 'N/A')}")
        
        with tab5:
            st.markdown("### 💳 Deudas y Obligaciones")
            
            deudas = parse_json_field(deputy_data.get('deudas_y_obligaciones'))
            if deudas:
                for deuda in deudas:
                    desc = deuda.get('descripcion', deuda.get('prestamo', 'Deuda'))
                    with st.expander(f"💳 {desc}"):
                        st.markdown(f"📅 **Fecha**: {deuda.get('fecha_concesion', 'N/A')}")
                        st.markdown(f"💰 **Importe original**: {format_currency(parse_currency_value(deuda.get('importe_concedido')))}")
                        st.markdown(f"💸 **Saldo pendiente**: {format_currency(parse_currency_value(deuda.get('saldo_pendiente')))}")
            else:
                st.success("✅ No hay deudas declaradas")
            
            # Observaciones
            if pd.notna(deputy_data.get('observaciones')) and deputy_data.get('observaciones'):
                st.markdown("### 📝 Observaciones")
                st.info(deputy_data.get('observaciones'))
            
            # Otros bienes
            otros = parse_json_field(deputy_data.get('otros_bienes_no_declarados_anteriormente'))
            if otros:
                st.markdown("### 📦 Otros Bienes")
                for item in otros:
                    desc = item.get('descripcion', 'N/A')
                    valor = format_currency(parse_currency_value(item.get('valor')))
                    st.markdown(f"• **{desc}**: {valor}")

if __name__ == "__main__":
    main()
