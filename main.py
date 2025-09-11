import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import re
import os

# Page configuration
st.set_page_config(
    page_title="Registro de Diputados",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced modern dark theme with gradient accents
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main App Styling */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #16213e 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main .block-container {
        padding-top: 1rem;
        max-width: 1600px;
    }
    
    /* Typography */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1.8rem !important;
    }
    
    h3 {
        color: #e2e8f0 !important;
        font-weight: 500 !important;
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(102, 126, 234, 0.2);
        backdrop-filter: blur(10px);
    }
    
    /* Deputy Card Container */
    .deputy-card {
        background: linear-gradient(135deg, rgba(30, 30, 60, 0.7) 0%, rgba(20, 20, 40, 0.9) 100%);
        border-radius: 24px;
        padding: 2.5rem;
        border: 2px solid rgba(102, 126, 234, 0.3);
        backdrop-filter: blur(12px);
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.4);
        margin-top: 1rem;
    }
    
    /* Image Gallery */
    .image-gallery {
        display: flex;
        gap: 1.5rem;
        margin-bottom: 2rem;
        align-items: center;
        justify-content: center;
    }
    
    .main-image-container {
        position: relative;
        flex: 0 0 auto;
    }
    
    .main-image {
        width: 220px;
        height: 280px;
        object-fit: cover;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        border: 2px solid rgba(102, 126, 234, 0.3);
    }
    
    .badge-container {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        align-items: center;
        justify-content: center;
    }
    
    .party-logo {
        width: 140px;
        height: 140px;
        object-fit: contain;
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .party-logo:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
    }
    
    .seat-indicator {
        width: 140px;
        height: 140px;
        object-fit: contain;
        background: rgba(102, 126, 234, 0.1);
        padding: 12px;
        border-radius: 10px;
        border: 1px solid rgba(102, 126, 234, 0.2);
        transition: all 0.3s ease;
    }
    
    .seat-indicator:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
    }
    
    /* Compact Info Grid */
    .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.2rem;
        margin: 1.5rem 0;
    }
    
    .info-item {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(102, 126, 234, 0.15);
        transition: all 0.3s ease;
    }
    
    .info-item:hover {
        transform: translateY(-2px);
        border-color: rgba(102, 126, 234, 0.3);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }
    
    .info-label {
        font-size: 0.8rem;
        color: #b4bdc8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .info-value {
        font-size: 1.1rem;
        color: #ffffff;
        font-weight: 500;
    }
    
    /* Enhanced Metrics */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.05) 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
        padding: 1rem;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.25);
        border-color: rgba(102, 126, 234, 0.4);
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: #94a3b8 !important;
        font-size: 0.7rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-weight: 600 !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #ffffff !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Improved Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(30, 30, 60, 0.3);
        border-radius: 12px;
        padding: 4px;
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        padding: 0 20px;
        background: transparent;
        border: none;
        border-radius: 8px;
        color: #94a3b8;
        font-size: 0.9rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff;
        background: rgba(102, 126, 234, 0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.25) 0%, rgba(118, 75, 162, 0.25) 100%);
        color: #ffffff !important;
        font-weight: 600;
    }
    
    /* Social Media Pills - Circular Emoji Buttons */
    .social-pills {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        margin-top: 1.2rem;
    }
    
    .social-pill {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        border: 2px solid rgba(102, 126, 234, 0.3);
        width: 55px;
        height: 55px;
        border-radius: 50%;
        font-size: 1.6rem;
        text-decoration: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        color: #ffffff;
        font-weight: bold;
    }
    
    .social-pill:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.35) 0%, rgba(118, 75, 162, 0.35) 100%);
        transform: translateY(-4px) scale(1.1);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.45);
        border-color: rgba(102, 126, 234, 0.6);
    }
    
    /* Expandable Cards */
    .stExpander {
        background: rgba(30, 30, 60, 0.3);
        border: 1px solid rgba(102, 126, 234, 0.15);
        border-radius: 12px;
        margin-bottom: 0.5rem;
    }
    
    .stExpander:hover {
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    /* Input Fields */
    .stSelectbox > div > div, .stTextInput > div > div > input {
        background: rgba(30, 30, 60, 0.4);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 10px;
        color: white;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover, .stTextInput > div > div > input:focus {
        border-color: rgba(102, 126, 234, 0.5);
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
    }
    
    /* Quick Stats Bar */
    .stats-bar {
        display: flex;
        gap: 1rem;
        padding: 1rem;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    .stat-item {
        flex: 1;
        text-align: center;
        padding: 0.5rem;
        border-right: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    .stat-item:last-child {
        border-right: none;
    }
    
    .stat-value {
        font-size: 1.2rem;
        font-weight: 600;
        color: #ffffff;
    }
    
    .stat-label {
        font-size: 0.7rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.25rem;
    }
    
    /* Hide Streamlit Elements */
    #MainMenu, footer, header { visibility: hidden; }
    .viewerBadge_container__1QSob { display: none; }
    
    /* Loading Animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess the deputies data"""
    df = pd.read_csv('deputies_full_dataset.csv', encoding='utf-8-sig')
    path_columns = ['photo_path', 'logo_path', 'hemiciclo_path']
    for col in path_columns:
        if col in df.columns:
            df[col] = df[col].str.replace('\\', '/', regex=False).str.strip()
    return df

def parse_json_field(field_value):
    """Safely parse JSON fields"""
    if pd.isna(field_value) or field_value in ('[]', ''):
        return []
    try:
        cleaned_value = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', str(field_value))
        return json.loads(cleaned_value)
    except:
        return []

def format_currency(value):
    """Format currency values for display with Spanish notation - exact values"""
    if not isinstance(value, (int, float)):
        return "0€"
    
    # Check if it's a whole number or has decimals
    if value == int(value):
        # No decimals needed - format with Spanish thousands separator
        formatted = f"{int(value):,}".replace(",", ".")
        return f"{formatted}€"
    else:
        # Show up to 2 decimal places with Spanish formatting
        formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{formatted}€"

def format_currency_full(value):
    """Format currency values for detailed display with Spanish formatting"""
    if not isinstance(value, (int, float)):
        return "0,00 €"
    
    # Show exact value with Spanish formatting
    if value == int(value):
        # If it's a whole number, show without decimals
        formatted = f"{int(value):,}".replace(",", ".")
        return f"{formatted} €"
    else:
        # Show with 2 decimal places
        formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{formatted} €"

def extract_currency_value(value_str):
    """Extract numeric value from currency string"""
    if pd.isna(value_str) or value_str == '':
        return 0
    if isinstance(value_str, (int, float)):
        return float(value_str)
    
    numeric_part = re.search(r'[\d.,]+', str(value_str))
    if numeric_part:
        try:
            cleaned_str = numeric_part.group(0).replace('.', '').replace(',', '.')
            return float(cleaned_str)
        except (ValueError, TypeError):
            return 0
    return 0

def create_image_gallery(deputy_data):
    """Create a compact image gallery for the deputy"""
    gallery_html = '<div class="image-gallery">'
    
    # Main photo
    gallery_html += '<div class="main-image-container">'
    photo_path = deputy_data.get('photo_path', '')
    if pd.notna(photo_path) and str(photo_path).lower() != 'nan' and os.path.exists(str(photo_path)):
        import base64
        with open(photo_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
            gallery_html += f'<img src="data:image/jpeg;base64,{img_data}" class="main-image" alt="Foto del Diputado">'
    else:
        gallery_html += '<div class="main-image" style="width: 220px; height: 280px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%); display: flex; flex-direction: column; align-items: center; justify-content: center; color: #94a3b8; font-size: 1.2rem; border-radius: 15px; border: 2px solid rgba(102, 126, 234, 0.3);">👤<br>Sin Foto</div>'
    gallery_html += '</div>'
    
    # Badges container
    gallery_html += '<div class="badge-container">'
    
    # Party logo
    logo_path = deputy_data.get('logo_path', '')
    if pd.notna(logo_path) and str(logo_path).lower() != 'nan' and os.path.exists(str(logo_path)):
        import base64
        with open(logo_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
            gallery_html += f'<img src="data:image/png;base64,{img_data}" class="party-logo" alt="Logo del Partido" title="Partido Político">'
    
    # Seat indicator
    hemiciclo_path = deputy_data.get('hemiciclo_path', '')
    if pd.notna(hemiciclo_path) and str(hemiciclo_path).lower() != 'nan' and os.path.exists(str(hemiciclo_path)):
        import base64
        with open(hemiciclo_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
            gallery_html += f'<img src="data:image/png;base64,{img_data}" class="seat-indicator" alt="Posición en el Hemiciclo" title="Escaño en el Hemiciclo">'
    
    gallery_html += '</div></div>'
    return gallery_html

def main():
    # Header with gradient
    st.markdown('<h1 style="text-align: center; margin-bottom: 0;">⚖️ Registro de Diputados</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #94a3b8; font-size: 1rem; margin-top: 0;">CONGRESO DE LOS DIPUTADOS · Portal de Transparencia Financiera</p>', unsafe_allow_html=True)
    
    df = load_data()
    
    # Search in a compact layout
    with st.container():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            search_term = st.text_input("🔍 Búsqueda", placeholder="Buscar diputado por nombre...", label_visibility="visible")
        
        # Filter data
        filtered_df = df.copy()
        if search_term:
            filtered_df = filtered_df[filtered_df['informacion_personal_nombre_y_apellidos'].str.contains(search_term, case=False, na=False)]
        
        with col2:
            st.metric("Resultados", f"{len(filtered_df)}", label_visibility="visible")
    
    st.markdown("---")
    
    if len(filtered_df) == 0:
        st.warning("🔍 No se encontraron diputados con ese criterio de búsqueda")
    else:
        # Deputy selector with better formatting
        deputy_names = filtered_df['informacion_personal_nombre_y_apellidos'].tolist()
        selected_deputy = st.selectbox(
            "**Seleccionar Diputado:**",
            deputy_names,
            format_func=lambda x: f"👤 {x}",
            label_visibility="visible"
        )
        
        deputy_data = filtered_df[filtered_df['informacion_personal_nombre_y_apellidos'] == selected_deputy].iloc[0]
        
        # Main Deputy Card
        st.markdown('<div class="deputy-card">', unsafe_allow_html=True)
        
        # Create two-column layout with image gallery on left
        col_left, col_right = st.columns([1.6, 2])
        
        with col_left:
            # Compact image gallery
            st.markdown(create_image_gallery(deputy_data), unsafe_allow_html=True)
            
            # Basic info in compact grid
            st.markdown("### 📋 Información Básica")
            
            # Build info grid dynamically, excluding 'nan' values
            info_html = '<div class="info-grid">'
            
            # Always show cargo, default to "Diputado" if empty
            cargo = deputy_data.get('informacion_personal_cargo', '')
            if not cargo or str(cargo).lower() == 'nan':
                cargo = 'Diputado'
            info_html += f'''
            <div class="info-item">
                <div class="info-label">📋 CARGO</div>
                <div class="info-value">{cargo}</div>
            </div>'''
            
            circunscripcion = deputy_data.get('informacion_personal_circunscripcion', '')
            if circunscripcion and str(circunscripcion).lower() != 'nan':
                info_html += f'''
                <div class="info-item">
                    <div class="info-label">📍 CIRCUNSCRIPCIÓN</div>
                    <div class="info-value">{circunscripcion}</div>
                </div>'''
            
            estado_civil = deputy_data.get('informacion_personal_estado_civil', '')
            if estado_civil and str(estado_civil).lower() != 'nan':
                info_html += f'''
                <div class="info-item">
                    <div class="info-label">💑 ESTADO CIVIL</div>
                    <div class="info-value">{estado_civil}</div>
                </div>'''
            
            fecha_eleccion = deputy_data.get('informacion_personal_fecha_eleccion', '')
            if fecha_eleccion and str(fecha_eleccion).lower() != 'nan':
                info_html += f'''
                <div class="info-item">
                    <div class="info-label">📅 FECHA DE ELECCIÓN</div>
                    <div class="info-value">{fecha_eleccion}</div>
                </div>'''
            
            info_html += '</div>'
            st.markdown(info_html, unsafe_allow_html=True)
            
            # Social Media Links as pills with emojis
            social_links = {
                "𝕏": deputy_data.get('twitter'),  # X/Twitter
                "📘": deputy_data.get('facebook'),  # Facebook
                "📸": deputy_data.get('instagram'),  # Instagram
                "🌐": deputy_data.get('website')  # Website
            }
            
            valid_links = {emoji: url for emoji, url in social_links.items() if pd.notna(url) and str(url).lower() != 'nan'}
            
            if valid_links:
                st.markdown("### 🌐 Redes Sociales")
                social_html = '<div class="social-pills">'
                
                # Map emojis to titles for hover text
                emoji_titles = {
                    "𝕏": "X (Twitter)",
                    "📘": "Facebook", 
                    "📸": "Instagram",
                    "🌐": "Sitio Web"
                }
                
                for emoji, url in valid_links.items():
                    title = emoji_titles.get(emoji, "")
                    social_html += f'<a href="{url}" target="_blank" class="social-pill" title="{title}">{emoji}</a>'
                social_html += '</div>'
                st.markdown(social_html, unsafe_allow_html=True)
        
        with col_right:
            # Deputy name with style
            st.markdown(f"## 👤 {deputy_data['informacion_personal_nombre_y_apellidos']}")
            
            # Calculate financial metrics
            salaries = parse_json_field(deputy_data['rentas_percibidas_percepciones_salariales'])
            total_salary = sum(extract_currency_value(s.get('euros', 0)) for s in salaries if isinstance(s, dict))
            
            if total_salary == 0:
                salary_text = str(deputy_data.get('rentas_percibidas_percepciones_salariales', ''))
                if "mensual" in salary_text.lower():
                    monthly_salary = extract_currency_value(salary_text)
                    total_salary = monthly_salary * 12
            
            irpf = extract_currency_value(deputy_data.get('irpf_cantidad_pagada', 0))
            tax_rate = (irpf / total_salary * 100) if total_salary > 0 else 0
            properties_count = len(parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos']))
            vehicles_count = len(parse_json_field(deputy_data['vehiculos']))
            debts = parse_json_field(deputy_data['deudas_y_obligaciones'])
            total_debt = sum(extract_currency_value(d.get('saldo_pendiente', 0)) for d in debts if isinstance(d, dict))
            
            # Financial Overview - Compact metrics with exact values
            st.markdown("### 💰 Resumen Financiero")
            metric_cols = st.columns(6)
            metric_cols[0].metric("Ingresos", format_currency(total_salary), help="Total de ingresos anuales declarados")
            metric_cols[1].metric("IRPF", format_currency(irpf), help="Impuesto sobre la renta pagado")
            metric_cols[2].metric("Tipo", f"{tax_rate:.2f}%", help="Tipo impositivo efectivo")
            metric_cols[3].metric("Inmuebles", str(properties_count), help="Número de propiedades")
            metric_cols[4].metric("Vehículos", str(vehicles_count), help="Número de vehículos")
            metric_cols[5].metric("Deudas", format_currency(total_debt), help="Deuda total pendiente")
            
            st.markdown("---")
            
            # Compact tabs
            tab1, tab2, tab3, tab4 = st.tabs(["💵 Ingresos", "🏠 Patrimonio", "💳 Deudas", "📊 Análisis"])
            
            with tab1:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 💼 Salarios e Ingresos")
                    salaries = parse_json_field(deputy_data['rentas_percibidas_percepciones_salariales'])
                    if salaries:
                        for i, salary in enumerate(salaries):
                            if isinstance(salary, dict):
                                concepto = salary.get('concepto', '')
                                if not concepto or str(concepto).lower() == 'nan':
                                    concepto = f'Fuente de Ingresos #{i+1}'
                                
                                with st.expander(f"💰 {concepto}"):
                                    amount = extract_currency_value(salary.get('euros'))
                                    display_amount = format_currency_full(amount)
                                    if "mensual" in str(salary.get('euros', '')).lower():
                                        display_amount += " (mensual)"
                                    st.markdown(f"**Importe:** {display_amount}")
                    else:
                        st.info("No se han declarado fuentes de ingresos")
                
                with col2:
                    st.markdown("#### 📈 Rentas del Capital")
                    dividends = parse_json_field(deputy_data['rentas_percibidas_dividendos_y_participaciones'])
                    if dividends:
                        for div in dividends:
                            if isinstance(div, dict):
                                concepto = div.get('concepto', '')
                                if not concepto or str(concepto).lower() == 'nan':
                                    concepto = 'Inversión'
                                
                                with st.expander(f"📊 {concepto}"):
                                    rendimientos = extract_currency_value(div.get('euros'))
                                    if rendimientos > 0:
                                        st.markdown(f"**Rendimientos:** {format_currency_full(rendimientos)}")
                    else:
                        st.info("No se han declarado rentas del capital")
            
            with tab2:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 🏠 Bienes Inmuebles")
                    urban = parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos'])
                    if urban:
                        for i, prop in enumerate(urban):
                            if isinstance(prop, dict):
                                with st.expander(f"🏢 Inmueble #{i+1}"):
                                    tipo = prop.get('clase_y_caracteristicas', '')
                                    if tipo and str(tipo).lower() != 'nan':
                                        st.markdown(f"**Tipo:** {tipo}")
                                    
                                    ubicacion = prop.get('situacion', '')
                                    if ubicacion and str(ubicacion).lower() != 'nan':
                                        st.markdown(f"**Ubicación:** {ubicacion}")
                                    
                                    fecha = prop.get('fecha_adquisicion', '')
                                    if fecha and str(fecha).lower() != 'nan':
                                        st.markdown(f"**Fecha Adquisición:** {fecha}")
                    else:
                        st.info("No se han declarado propiedades")
                    
                    st.markdown("#### 💳 Activos Financieros")
                    accounts = parse_json_field(deputy_data['depositos_y_cuentas_cuentas'])
                    if accounts:
                        for i, account in enumerate(accounts):
                            if isinstance(account, dict):
                                desc = account.get('descripcion', '')
                                if not desc or str(desc).lower() == 'nan':
                                    desc = f'Cuenta #{i+1}'
                                
                                with st.expander(f"🏦 {desc}"):
                                    saldo = extract_currency_value(account.get('saldo'))
                                    if saldo > 0:
                                        st.markdown(f"**Saldo:** {format_currency_full(saldo)}")
                    else:
                        st.info("No se han declarado cuentas")
                
                with col2:
                    st.markdown("#### 🚗 Vehículos")
                    vehicles = parse_json_field(deputy_data['vehiculos'])
                    if vehicles:
                        for i, vehicle in enumerate(vehicles):
                            if isinstance(vehicle, dict):
                                desc = vehicle.get('descripcion', f'Vehículo #{i+1}')
                                with st.expander(f"🚙 {desc}"):
                                    fecha = vehicle.get('fecha_adquisicion', '')
                                    if fecha and str(fecha).lower() != 'nan':
                                        st.markdown(f"**Fecha Adquisición:** {fecha}")
                    else:
                        st.info("No se han declarado vehículos")
            
            with tab3:
                st.markdown("#### 💸 Deudas y Obligaciones")
                if debts:
                    # Summary card
                    st.info(f"**Deuda Total Pendiente:** {format_currency_full(total_debt)}")
                    
                    for i, debt in enumerate(debts):
                        if isinstance(debt, dict):
                            desc = debt.get('descripcion', '')
                            if not desc or str(desc).lower() == 'nan':
                                desc = f'Deuda #{i+1}'
                            
                            with st.expander(f"📄 {desc}"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    importe_original = extract_currency_value(debt.get('importe_concedido'))
                                    if importe_original > 0:
                                        st.markdown(f"**Importe Original:** {format_currency_full(importe_original)}")
                                    
                                    fecha = debt.get('fecha_concesion', '')
                                    if fecha and str(fecha).lower() != 'nan':
                                        st.markdown(f"**Fecha Concesión:** {fecha}")
                                
                                with col2:
                                    importe_pendiente = extract_currency_value(debt.get('saldo_pendiente'))
                                    if importe_pendiente > 0:
                                        st.markdown(f"**Importe Pendiente:** {format_currency_full(importe_pendiente)}")
                                    
                                    original = extract_currency_value(debt.get('importe_concedido'))
                                    pending = extract_currency_value(debt.get('saldo_pendiente'))
                                    if original > 0:
                                        paid_pct = ((original - pending) / original) * 100
                                        st.markdown(f"**Pagado:** {paid_pct:.2f}%")
                else:
                    st.success("✅ No se han declarado deudas")
            
            with tab4:
                st.markdown("#### 📊 Análisis Financiero")
                
                # Create analysis visualizations
                col1, col2 = st.columns(2)
                
                with col1:
                    # Asset Distribution Pie Chart
                    fig_assets = go.Figure(data=[go.Pie(
                        labels=['Propiedades', 'Vehículos', 'Efectivo/Cuentas'],
                        values=[
                            properties_count * 150000,  # Estimated avg property value
                            vehicles_count * 20000,     # Estimated avg vehicle value
                            sum(extract_currency_value(a.get('saldo', 0)) for a in parse_json_field(deputy_data['depositos_y_cuentas_cuentas']) if isinstance(a, dict))
                        ],
                        hole=.3,
                        marker_colors=['#667eea', '#764ba2', '#f093fb']
                    )])
                    fig_assets.update_layout(
                        title="Distribución de Patrimonio (Estimado)",
                        showlegend=True,
                        height=300,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    )
                    st.plotly_chart(fig_assets, use_container_width=True)
                
                with col2:
                    # Tax Efficiency Gauge with exact value
                    fig_tax = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=tax_rate,
                        number={'suffix': "%", 'valueformat': ".2f"},
                        title={'text': "Tipo Impositivo Efectivo"},
                        domain={'x': [0, 1], 'y': [0, 1]},
                        gauge={
                            'axis': {'range': [None, 50]},
                            'bar': {'color': "#667eea"},
                            'steps': [
                                {'range': [0, 15], 'color': "rgba(102, 126, 234, 0.1)"},
                                {'range': [15, 30], 'color': "rgba(102, 126, 234, 0.2)"},
                                {'range': [30, 50], 'color': "rgba(102, 126, 234, 0.3)"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 30
                            }
                        }
                    ))
                    fig_tax.update_layout(
                        height=300,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    )
                    st.plotly_chart(fig_tax, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
