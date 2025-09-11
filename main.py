import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import re
import os
import base64

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="Registro de Diputados",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for disclaimer
if 'disclaimer_accepted' not in st.session_state:
    st.session_state.disclaimer_accepted = False

# Enhanced CSS with better specificity and responsive design
def apply_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Root variables for consistent theming */
        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --bg-gradient: linear-gradient(180deg, #0f0f23 0%, #1a1a3e 100%);
            --glass-bg: rgba(255, 255, 255, 0.05);
            --glass-border: rgba(255, 255, 255, 0.1);
            --text-primary: #ffffff;
            --text-secondary: #e2e8f0;
            --text-muted: #94a3b8;
        }
        
        /* Force dark background on main container */
        .stApp {
            background: var(--bg-gradient) !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            min-height: 100vh;
        }
        
        /* Main content area */
        .main {
            background: transparent !important;
        }
        
        .block-container {
            padding: 1rem !important;
            max-width: 1600px !important;
            margin: 0 auto !important;
        }
        
        /* Fix Streamlit's default white backgrounds */
        [data-testid="stAppViewContainer"] {
            background: transparent !important;
        }
        
        [data-testid="stHeader"] {
            background: transparent !important;
        }
        
        [data-testid="stToolbar"] {
            display: none !important;
        }
        
        /* Typography */
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-primary) !important;
        }
        
        .main h1 {
            background: var(--primary-gradient) !important;
            background-clip: text !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            font-weight: 700 !important;
            font-size: clamp(1.5rem, 4vw, 2.5rem) !important;
            text-align: center;
            margin-bottom: 0.5rem !important;
        }
        
        .main h2 {
            color: var(--text-primary) !important;
            font-size: clamp(1.2rem, 3vw, 1.8rem) !important;
        }
        
        .main h3 {
            color: var(--text-secondary) !important;
            font-size: clamp(1rem, 2.5vw, 1.4rem) !important;
        }
        
        p, span, div {
            color: var(--text-secondary);
        }
        
        /* Disclaimer Container */
        .disclaimer-container {
            background: var(--glass-bg) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border: 2px solid var(--glass-border) !important;
            border-radius: 20px;
            padding: clamp(1.5rem, 4vw, 3rem);
            margin: 2rem auto;
            max-width: min(800px, 90vw);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }
        
        .disclaimer-title {
            font-size: clamp(1.5rem, 4vw, 2rem);
            font-weight: 700;
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .disclaimer-text {
            color: var(--text-secondary);
            font-size: clamp(0.9rem, 2vw, 1.1rem);
            line-height: 1.8;
            text-align: justify;
        }
        
        /* Info Grid - Responsive */
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(min(250px, 100%), 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }
        
        .info-item {
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 1rem;
            border-radius: 12px;
            border: 1px solid var(--glass-border);
            transition: all 0.3s ease;
        }
        
        .info-item:hover {
            transform: translateY(-5px);
            border-color: rgba(102, 126, 234, 0.4);
            box-shadow: 0 12px 40px rgba(102, 126, 234, 0.3);
        }
        
        .info-label {
            font-size: clamp(0.7rem, 1.5vw, 0.8rem);
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }
        
        .info-value {
            font-size: clamp(0.9rem, 2vw, 1.1rem);
            color: var(--text-primary);
            font-weight: 500;
        }
        
        /* Social Pills - Responsive */
        .social-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin-top: 1rem;
            justify-content: center;
        }
        
        .social-pill {
            background: var(--glass-bg);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 2px solid var(--glass-border);
            width: clamp(40px, 8vw, 50px);
            height: clamp(40px, 8vw, 50px);
            border-radius: 50%;
            font-size: clamp(1.2rem, 3vw, 1.5rem);
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }
        
        .social-pill:hover {
            background: rgba(102, 126, 234, 0.2);
            transform: scale(1.2);
            border-color: rgba(102, 126, 234, 0.5);
        }
        
        /* Streamlit Components - Dark Theme */
        .stSelectbox > div > div {
            background-color: var(--glass-bg) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: 10px !important;
            color: var(--text-primary) !important;
        }
        
        .stTextInput > div > div > input {
            background-color: var(--glass-bg) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: 10px !important;
            color: var(--text-primary) !important;
        }
        
        /* Selectbox dropdown fix */
        [data-baseweb="select"] {
            background-color: var(--glass-bg) !important;
        }
        
        [data-baseweb="select"] > div {
            background-color: var(--glass-bg) !important;
            border-color: var(--glass-border) !important;
        }
        
        /* Option menu styling */
        [role="listbox"] {
            background-color: #1a1a3e !important;
        }
        
        [role="option"] {
            background-color: #1a1a3e !important;
            color: var(--text-primary) !important;
        }
        
        [role="option"]:hover {
            background-color: rgba(102, 126, 234, 0.2) !important;
        }
        
        /* Metrics */
        [data-testid="metric-container"] {
            background: var(--glass-bg) !important;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            padding: 1rem;
            border-radius: 16px;
            transition: all 0.3s ease;
        }
        
        [data-testid="metric-container"]:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 50px rgba(102, 126, 234, 0.4);
        }
        
        [data-testid="metric-container"] label {
            color: var(--text-muted) !important;
            font-size: clamp(0.7rem, 1.5vw, 0.75rem) !important;
        }
        
        [data-testid="metric-container"] [data-testid="metric-value"] {
            color: var(--text-primary) !important;
            font-size: clamp(1.2rem, 3vw, 1.8rem) !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background: var(--glass-bg);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 6px;
            border: 1px solid var(--glass-border);
            flex-wrap: wrap;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            color: var(--text-muted);
            border: none;
            font-size: clamp(0.75rem, 1.8vw, 0.85rem);
            padding: 0.5rem 1rem;
            white-space: nowrap;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            color: var(--text-primary);
            background: rgba(102, 126, 234, 0.1);
        }
        
        .stTabs [aria-selected="true"] {
            background: rgba(102, 126, 234, 0.2) !important;
            color: var(--text-primary) !important;
        }
        
        /* Buttons */
        .stButton > button {
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            color: var(--text-primary);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 8px;
            transition: all 0.3s ease;
            font-size: clamp(0.9rem, 2vw, 1rem);
            padding: 0.5rem 1rem;
        }
        
        .stButton > button:hover {
            background: rgba(102, 126, 234, 0.2);
            border-color: rgba(102, 126, 234, 0.5);
            transform: translateY(-2px);
        }
        
        /* Success/Warning/Error messages */
        .stSuccess, .stWarning, .stError, .stInfo {
            background: var(--glass-bg) !important;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 12px;
            color: var(--text-primary) !important;
        }
        
        /* Hide Streamlit elements */
        #MainMenu, footer, header {
            visibility: hidden !important;
        }
        
        /* Mobile Responsive */
        @media (max-width: 768px) {
            .block-container {
                padding: 0.5rem !important;
            }
            
            .info-grid {
                grid-template-columns: 1fr;
            }
            
            .stTabs [data-baseweb="tab-list"] {
                gap: 2px;
            }
            
            .stTabs [data-baseweb="tab"] {
                font-size: 0.7rem;
                padding: 0.4rem 0.6rem;
            }
        }
        
        /* Tablet Responsive */
        @media (min-width: 769px) and (max-width: 1024px) {
            .info-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        /* Force dark theme on all text */
        * {
            color: var(--text-secondary);
        }
        
        /* Plotly chart dark theme */
        .js-plotly-plot .plotly {
            background: transparent !important;
        }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess the deputies data"""
    try:
        df = pd.read_csv('deputies_full_dataset.csv', encoding='utf-8-sig')
        path_columns = ['photo_path', 'logo_path', 'hemiciclo_path']
        for col in path_columns:
            if col in df.columns:
                df[col] = df[col].str.replace('\\', '/', regex=False).str.strip()
        return df
    except FileNotFoundError:
        st.error("⚠️ No se encontró el archivo 'deputies_full_dataset.csv'.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        return pd.DataFrame()

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
    """Format currency values for display with Spanish notation"""
    if not isinstance(value, (int, float)):
        return "0€"
    
    if value == int(value):
        formatted = f"{int(value):,}".replace(",", ".")
        return f"{formatted}€"
    else:
        formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{formatted}€"

def format_currency_full(value):
    """Format currency values for detailed display"""
    if not isinstance(value, (int, float)):
        return "0,00 €"
    
    if value == int(value):
        formatted = f"{int(value):,}".replace(",", ".")
        return f"{formatted} €"
    else:
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

def get_base64_image(image_path):
    """Convert image to base64 string"""
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

def create_responsive_image_gallery(deputy_data):
    """Create responsive image gallery HTML"""
    gallery_html = '''
    <div style="display: flex; flex-wrap: wrap; gap: 1rem; align-items: center; 
                justify-content: center; margin-bottom: 2rem;">
    '''
    
    # Main photo
    photo_path = deputy_data.get('photo_path', '')
    if pd.notna(photo_path) and str(photo_path).lower() != 'nan' and os.path.exists(str(photo_path)):
        img_data = get_base64_image(photo_path)
        if img_data:
            gallery_html += f'''
            <div style="flex: 0 1 200px;">
                <img src="data:image/jpeg;base64,{img_data}" 
                     style="width: 100%; max-width: 200px; height: auto; 
                            aspect-ratio: 4/5; object-fit: cover; 
                            border-radius: 12px; 
                            border: 2px solid rgba(102, 126, 234, 0.3);">
            </div>'''
    else:
        gallery_html += '''
        <div style="flex: 0 1 200px;">
            <div style="width: 100%; max-width: 200px; aspect-ratio: 4/5; 
                        background: rgba(102, 126, 234, 0.1); 
                        display: flex; align-items: center; justify-content: center; 
                        color: #94a3b8; border-radius: 12px; 
                        border: 2px solid rgba(102, 126, 234, 0.3);">
                👤<br>Sin Foto
            </div>
        </div>'''
    
    # Badges container
    gallery_html += '''
    <div style="display: flex; flex-direction: column; gap: 1rem; 
                align-items: center; flex: 0 1 auto;">
    '''
    
    # Party logo
    logo_path = deputy_data.get('logo_path', '')
    if pd.notna(logo_path) and str(logo_path).lower() != 'nan' and os.path.exists(str(logo_path)):
        img_data = get_base64_image(logo_path)
        if img_data:
            gallery_html += f'''
            <img src="data:image/png;base64,{img_data}" 
                 style="width: 100%; max-width: 120px; height: auto; 
                        max-height: 120px; object-fit: contain; 
                        background: rgba(255, 255, 255, 0.05); 
                        padding: 10px; border-radius: 10px;">'''
    
    # Seat indicator
    hemiciclo_path = deputy_data.get('hemiciclo_path', '')
    if pd.notna(hemiciclo_path) and str(hemiciclo_path).lower() != 'nan' and os.path.exists(str(hemiciclo_path)):
        img_data = get_base64_image(hemiciclo_path)
        if img_data:
            gallery_html += f'''
            <img src="data:image/png;base64,{img_data}" 
                 style="width: 100%; max-width: 120px; height: auto; 
                        max-height: 120px; object-fit: contain; 
                        background: rgba(102, 126, 234, 0.1); 
                        padding: 10px; border-radius: 10px;">'''
    
    gallery_html += '</div></div>'
    return gallery_html

def show_disclaimer():
    """Show the legal disclaimer page"""
    apply_css()
    
    # Use container for better mobile layout
    container = st.container()
    
    with container:
        st.markdown("""
        <div class="disclaimer-container">
            <h1 class="disclaimer-title">⚖️ DESCARGO DE RESPONSABILIDAD</h1>
            <div class="disclaimer-text">
                <p>Esta aplicación recopila y organiza información pública disponible en la página web del Congreso de los Diputados. 
                La aplicación no pertenece ni está vinculada al Congreso de los Diputados.</p>
                
                <p>El contenido se ofrece únicamente con fines informativos. 
                <strong>Puede contener errores o información desactualizada</strong>. 
                Para consultas oficiales, acuda a la web del Congreso.</p>
                
                <p>El uso de esta aplicación es responsabilidad del usuario.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Center button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✅ ACEPTO Y ENTIENDO", type="primary", use_container_width=True):
                st.session_state.disclaimer_accepted = True
                st.rerun()

def main_app():
    """Main application with responsive design"""
    apply_css()
    
    st.markdown('<h1>⚖️ Registro de Diputados</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #94a3b8;">CONGRESO DE LOS DIPUTADOS</p>', 
                unsafe_allow_html=True)
    
    df = load_data()
    if df.empty:
        st.stop()
    
    # Get unique deputies
    unique_deputies = df.groupby('informacion_personal_nombre_y_apellidos').first().reset_index()
    
    # Search bar with responsive columns
    search_col, metric_col = st.columns([3, 1])
    
    with search_col:
        search_term = st.text_input("🔍 Búsqueda", placeholder="Buscar diputado...")
    
    # Filter deputies
    filtered_deputies = unique_deputies.copy()
    if search_term:
        mask = filtered_deputies['informacion_personal_nombre_y_apellidos'].str.contains(
            search_term, case=False, na=False)
        filtered_deputies = filtered_deputies[mask]
    
    with metric_col:
        st.metric("Total", len(filtered_deputies))
    
    st.markdown("---")
    
    if len(filtered_deputies) == 0:
        st.warning("🔍 No se encontraron diputados")
    else:
        # Deputy selector
        deputy_names = filtered_deputies['informacion_personal_nombre_y_apellidos'].tolist()
        selected_deputy_name = st.selectbox(
            "Seleccionar Diputado:",
            deputy_names,
            format_func=lambda x: f"👤 {x}"
        )
        
        # Get all declarations
        deputy_declarations = df[df['informacion_personal_nombre_y_apellidos'] == selected_deputy_name]
        
        # Declaration selector if multiple
        if len(deputy_declarations) > 1:
            st.info(f"📋 {len(deputy_declarations)} declaraciones disponibles")
            
            declaration_options = []
            for idx, row in deputy_declarations.iterrows():
                declaration_number = idx - deputy_declarations.index[0] + 1
                label = f"📄 Declaración {declaration_number}"
                
                fecha_eleccion = row.get('informacion_personal_fecha_eleccion', '')
                if fecha_eleccion and str(fecha_eleccion).lower() != 'nan':
                    label += f" - {fecha_eleccion}"
                    
                declaration_options.append((idx, label))
            
            selected_idx = st.selectbox(
                "Seleccionar:",
                [opt[0] for opt in declaration_options],
                format_func=lambda x: next(opt[1] for opt in declaration_options if opt[0] == x)
            )
            
            deputy_data = deputy_declarations.loc[selected_idx]
        else:
            deputy_data = deputy_declarations.iloc[0]
        
        st.markdown("---")
        
        # Responsive layout
        # On mobile, stack vertically. On desktop, use columns
        col_left, col_right = st.columns([1, 1.5])
        
        with col_left:
            # Image gallery
            st.markdown(create_responsive_image_gallery(deputy_data), unsafe_allow_html=True)
            
            # Basic info
            st.markdown("### 📋 Información")
            
            info_html = '<div class="info-grid">'
            
            personal_fields = [
                ('📍 CIRCUNSCRIPCIÓN', 'informacion_personal_circunscripcion'),
                ('💑 ESTADO CIVIL', 'informacion_personal_estado_civil'),
                ('📅 ELECCIÓN', 'informacion_personal_fecha_eleccion'),
            ]
            
            for label, field in personal_fields:
                value = deputy_data.get(field)
                if value and str(value).lower() != 'nan':
                    info_html += f'''
                    <div class="info-item">
                        <div class="info-label">{label}</div>
                        <div class="info-value">{value}</div>
                    </div>'''
            
            info_html += '</div>'
            st.markdown(info_html, unsafe_allow_html=True)
            
            # Social Media
            social_links = {
                "𝕏": deputy_data.get('twitter'),
                "📘": deputy_data.get('facebook'),
                "📸": deputy_data.get('instagram'),
                "🌐": deputy_data.get('website')
            }
            
            valid_links = {k: v for k, v in social_links.items() 
                          if pd.notna(v) and str(v).lower() != 'nan'}
            
            if valid_links:
                st.markdown("### 🌐 Redes")
                social_html = '<div class="social-pills">'
                for emoji, url in valid_links.items():
                    social_html += f'<a href="{url}" target="_blank" class="social-pill">{emoji}</a>'
                social_html += '</div>'
                st.markdown(social_html, unsafe_allow_html=True)
        
        with col_right:
            st.markdown(f"## {deputy_data['informacion_personal_nombre_y_apellidos']}")
            
            # Calculate metrics
            salaries = parse_json_field(deputy_data['rentas_percibidas_percepciones_salariales'])
            total_salary = sum(extract_currency_value(s.get('euros', 0)) 
                             for s in salaries if isinstance(s, dict))
            
            irpf = extract_currency_value(deputy_data.get('irpf_cantidad_pagada', 0))
            tax_rate = (irpf / total_salary * 100) if total_salary > 0 else 0
            
            # Properties
            urban_properties = len(parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos']))
            rustic_properties = len(parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_rusticos']))
            total_properties = urban_properties + rustic_properties
            
            vehicles_count = len(parse_json_field(deputy_data['vehiculos']))
            
            debts = parse_json_field(deputy_data['deudas_y_obligaciones'])
            total_debt = sum(extract_currency_value(d.get('saldo_pendiente', 0)) 
                           for d in debts if isinstance(d, dict))
            
            # Financial summary - Responsive metrics
            st.markdown("### 💰 Resumen Financiero")
            
            metrics_cols = st.columns([1, 1, 1])
            
            with metrics_cols[0]:
                st.metric("💵 Ingresos", format_currency(total_salary))
            
            with metrics_cols[1]:
                st.metric("🏠 Patrimonio", f"{total_properties + vehicles_count}")
            
            with metrics_cols[2]:
                st.metric("💳 Deudas", format_currency(total_debt))
            
            st.markdown("---")
            
            # Responsive tabs
            tab_list = ["💵 Ingresos", "🏠 Inmuebles", "💼 Sociedades", 
                       "🚗 Vehículos", "💳 Deudas"]
            tabs = st.tabs(tab_list)
            
            # TAB 1: INGRESOS
            with tabs[0]:
                st.markdown("#### 💵 Fuentes de Ingresos")
                
                if total_salary > 0:
                    st.success(f"Total Anual: **{format_currency_full(total_salary)}**")
                    if irpf > 0:
                        st.info(f"IRPF: **{format_currency_full(irpf)}** ({tax_rate:.1f}%)")
                
                # Show salaries
                if salaries:
                    for salary in salaries:
                        if isinstance(salary, dict):
                            concepto = salary.get('concepto', 'Ingreso')
                            amount = extract_currency_value(salary.get('euros'))
                            st.markdown(f"• **{concepto}**: {format_currency_full(amount)}")
                else:
                    st.info("Sin salarios declarados")
            
            # TAB 2: INMUEBLES
            with tabs[1]:
                st.markdown("#### 🏠 Bienes Inmuebles")
                
                urban = parse_json_field(deputy_data['bienes_patrimoniales_inmuebles_urbanos'])
                if urban:
                    st.markdown(f"**Urbanos:** {len(urban)}")
                
                rusticos = parse_json_field(deputy_data.get('bienes_patrimoniales_inmuebles_rusticos', ''))
                if rusticos:
                    st.markdown(f"**Rústicos:** {len(rusticos)}")
                
                if not urban and not rusticos:
                    st.info("Sin inmuebles declarados")
            
            # TAB 3: SOCIEDADES
            with tabs[2]:
                st.markdown("#### 💼 Sociedades")
                
                sociedades = parse_json_field(deputy_data.get('bienes_patrimoniales_bienes_sociedades_no_cotizadas', ''))
                if sociedades:
                    st.markdown(f"**Total:** {len(sociedades)} sociedades")
                else:
                    st.info("Sin sociedades declaradas")
            
            # TAB 4: VEHÍCULOS
            with tabs[3]:
                st.markdown("#### 🚗 Vehículos")
                
                vehicles = parse_json_field(deputy_data['vehiculos'])
                if vehicles:
                    st.info(f"Total: **{len(vehicles)}** vehículos")
                    for vehicle in vehicles:
                        if isinstance(vehicle, dict):
                            desc = vehicle.get('descripcion', 'Vehículo')
                            st.markdown(f"• {desc}")
                else:
                    st.info("Sin vehículos declarados")
            
            # TAB 5: DEUDAS
            with tabs[4]:
                st.markdown("#### 💳 Deudas")
                
                if debts:
                    st.error(f"Total Pendiente: **{format_currency_full(total_debt)}**")
                    for debt in debts:
                        if isinstance(debt, dict):
                            desc = debt.get('descripcion', 'Deuda')
                            pending = extract_currency_value(debt.get('saldo_pendiente'))
                            if pending > 0:
                                st.markdown(f"• **{desc}**: {format_currency_full(pending)}")
                else:
                    st.success("✅ Sin deudas declaradas")

# Main execution
if __name__ == "__main__":
    if not st.session_state.disclaimer_accepted:
        show_disclaimer()
    else:
        main_app()
