import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from pathlib import Path
import glob

# Page configuration - MUST BE FIRST
st.set_page_config(
    page_title="Declaraciones de Bienes y Rentas | XV Legislatura",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Spectacular dark mode CSS with glassmorphism and gradients
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Dark mode base */
    .stApp {
        background: linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Disclaimer with glassmorphism */
    .disclaimer-glass {
        background: rgba(255, 193, 7, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 193, 7, 0.2);
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
        color: #ffc107;
        box-shadow: 0 8px 32px 0 rgba(255, 193, 7, 0.1);
    }
    
    /* Hero section */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 50px 40px;
        border-radius: 30px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: "";
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    .hero-title {
        color: white;
        font-size: 2.8rem;
        font-weight: 900;
        margin-bottom: 10px;
        letter-spacing: -1px;
        position: relative;
        z-index: 1;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .hero-subtitle {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 25px;
        position: relative;
        z-index: 1;
        letter-spacing: 0.5px;
    }
    
    /* Individual card with glassmorphism */
    .individual-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        backdrop-filter: blur(10px);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 25px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.2);
        transition: all 0.3s ease;
    }
    
    .individual-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 50px rgba(102, 126, 234, 0.3);
    }
    
    /* Metric containers with animations */
    .metric-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        height: 100%;
        transition: all 0.3s ease;
    }
    
    .metric-container:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: translateY(-5px);
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 10px 0;
    }
    
    .metric-label {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Photo containers */
    .photo-main {
        max-width: 200px;
        margin: 0 auto;
    }
    
    .deputy-photo {
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        width: 100%;
        height: auto;
        transition: transform 0.3s ease;
    }
    
    .deputy-photo:hover {
        transform: scale(1.05);
    }
    
    .party-logo {
        max-width: 100px;
        height: auto;
        filter: drop-shadow(0 5px 15px rgba(0,0,0,0.3));
    }
    
    /* Comparison card */
    .comparison-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .comparison-card:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    /* Data tables with glassmorphism */
    .dataframe {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 15px;
    }
    
    .dataframe tbody tr:hover {
        background: rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Section headers */
    h1, h2, h3 {
        color: white !important;
        font-weight: 800 !important;
    }
    
    /* Tabs with animations */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        padding: 5px;
        gap: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: rgba(255, 255, 255, 0.6);
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-2px);
        color: white;
    }
    
    /* Buttons with gradient */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
    
    /* Select boxes and inputs */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    .stTextInput > div > div {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    /* Comparison header */
    .vs-header {
        text-align: center;
        font-size: 2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 20px 0;
    }
    
    /* Info cards */
    .info-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
        border-left: 4px solid #667eea;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    /* Animated background elements */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
        100% { transform: translateY(0px); }
    }
    
    .float-animation {
        animation: float 6s ease-in-out infinite;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'disclaimer_accepted' not in st.session_state:
    st.session_state.disclaimer_accepted = False
if 'comparison_mode' not in st.session_state:
    st.session_state.comparison_mode = False

# Helper functions
def parse_money_value(value):
    """Convert string money values to float"""
    if value is None or value == '':
        return 0
    if isinstance(value, (int, float)):
        return float(value)
    value_str = str(value).replace('€', '').replace('.', '').replace(',', '.')
    value_str = value_str.strip()
    try:
        return float(value_str)
    except:
        return 0

def get_deputy_photo(deputy_index):
    """Get the actual deputy photo"""
    photo_path = f"deputy_photos/deputy_{deputy_index:03d}.jpg"
    if os.path.exists(photo_path):
        return photo_path
    return None

def get_party_logo(constituency, name):
    """Determine party from constituency/name and get logo"""
    # You can implement party detection logic here
    # For now, returning a placeholder path
    party_logos = {
        'PP': 'fotos_diputados/pp_logo.png',
        'PSOE': 'fotos_diputados/psoe_logo.png',
        'VOX': 'fotos_diputados/vox_logo.png',
        'SUMAR': 'fotos_diputados/sumar_logo.png'
    }
    # Add logic to determine party from name/constituency
    return None

def get_hemiciclo_seat(deputy_index):
    """Get hemiciclo seat visualization"""
    pattern = f"hemiciclo/hemi_{deputy_index:04d}_*.gif"
    files = glob.glob(pattern)
    if files:
        return files[0]
    return None

# Load JSON data - without cache decorator to avoid tokenization issues
def load_json_data():
    try:
        with open('all_deputies_merged.json', 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        processed_data = []
        
        for idx, entry in enumerate(json_data, 1):
            if 'data' in entry and entry['data']:
                data = entry['data']
                personal_info = data.get('informacion_personal', {})
                
                # Calculate totals
                total_income = 0
                rentas = data.get('rentas_percibidas', {})
                
                for salary in rentas.get('percepciones_salariales', []):
                    total_income += parse_money_value(salary.get('euros', 0))
                for dividend in rentas.get('dividendos_y_participaciones', []):
                    total_income += parse_money_value(dividend.get('euros', 0))
                for interest in rentas.get('intereses_financieros', []):
                    total_income += parse_money_value(interest.get('euros', 0))
                for other in rentas.get('otras_rentas', []):
                    total_income += parse_money_value(other.get('euros', 0))
                
                # Liquid assets
                liquid_assets = 0
                accounts = data.get('depositos_y_cuentas', {}).get('cuentas', [])
                for account in accounts:
                    liquid_assets += parse_money_value(account.get('saldo', 0))
                
                # Debt
                total_debt = 0
                debts = data.get('deudas_y_obligaciones', [])
                for debt in debts:
                    total_debt += parse_money_value(debt.get('saldo_pendiente', 0))
                
                # Properties
                urban_properties = len(data.get('bienes_patrimoniales', {}).get('inmuebles_urbanos', []))
                rustic_properties = len(data.get('bienes_patrimoniales', {}).get('inmuebles_rusticos', []))
                vehicles_count = len(data.get('vehiculos', []))
                
                processed_data.append({
                    'deputy_index': idx,
                    'Nombre': personal_info.get('nombre_y_apellidos', '').upper(),
                    'Cargo': personal_info.get('cargo', 'Diputado'),
                    'Circunscripción': personal_info.get('circunscripcion', ''),
                    'Estado Civil': personal_info.get('estado_civil', ''),
                    'Régimen Económico': personal_info.get('regimen_economico_matrimonial', ''),
                    'Ingresos Declarados': total_income,
                    'Activos Líquidos': liquid_assets,
                    'Deudas': total_debt,
                    'Posición Neta': liquid_assets - total_debt,
                    'IRPF Pagado': parse_money_value(data.get('irpf', {}).get('cantidad_pagada', 0)),
                    'Propiedades Urbanas': urban_properties,
                    'Propiedades Rústicas': rustic_properties,
                    'Total Propiedades': urban_properties + rustic_properties,
                    'Vehículos': vehicles_count,
                })
        
        return pd.DataFrame(processed_data)
        
    except FileNotFoundError:
        st.error("No se encuentra el archivo 'all_deputies_merged.json'")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al procesar el archivo: {str(e)}")
        return pd.DataFrame()

# Disclaimer with spectacular design
if not st.session_state.disclaimer_accepted:
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">DECLARACIONES DE BIENES Y RENTAS</h1>
        <p class="hero-subtitle">XV Legislatura - Congreso de los Diputados</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="disclaimer-glass">
        <h2 style="color: #ffc107; text-align: center; margin-bottom: 20px;">⚠️ Descargo de Responsabilidad</h2>
        <p style="line-height: 1.8;">
            Esta aplicación es una herramienta independiente de visualización de información pública.
            No tiene vinculación con el Congreso de los Diputados. Los datos pueden contener errores.
            Para información oficial, consulte el portal del Congreso de los Diputados.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✅ Aceptar y Continuar", use_container_width=True, type="primary"):
            st.session_state.disclaimer_accepted = True
            st.rerun()
    
    st.stop()

# Main App - Hero Section
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">DECLARACIONES DE BIENES Y RENTAS</h1>
    <p class="hero-subtitle">XV Legislatura - Congreso de los Diputados</p>
    <a href="https://twitter.com/Gsnchez" target="_blank" style="display: inline-block; background: rgba(255, 255, 255, 0.2); backdrop-filter: blur(10px); padding: 12px 24px; border-radius: 50px; color: white; font-weight: 600; text-decoration: none; transition: all 0.3s ease; position: relative; z-index: 1;">
        Desarrollado por @Gsnchez ✨
    </a>
</div>
""", unsafe_allow_html=True)

# Load data
df = load_json_data()

if not df.empty:
    # Main tabs
    tab1, tab2 = st.tabs(["🔍 Análisis Individual", "📊 Tabla de Datos Completa"])
    
    with tab1:
        st.markdown("### 🔍 Análisis Individual de Parlamentarios")
        
        # Comparison mode toggle
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            comparison_mode = st.checkbox("📊 Modo Comparación", value=st.session_state.comparison_mode)
            st.session_state.comparison_mode = comparison_mode
        
        if not comparison_mode:
            # Single deputy analysis
            col1, col2 = st.columns([3, 1])
            with col1:
                search_term = st.text_input("🔎 Buscar por nombre:", placeholder="Introduzca el nombre del parlamentario...")
            
            # Filter names
            if search_term:
                filtered_df = df[df['Nombre'].str.contains(search_term, case=False, na=False)]
                names = sorted(filtered_df['Nombre'].unique())
            else:
                names = sorted(df['Nombre'].unique())
            
            if names:
                selected_name = st.selectbox("Seleccione parlamentario:", names, key="single_select")
                
                if selected_name:
                    person_data = df[df['Nombre'] == selected_name].iloc[0]
                    
                    # Main info card with photos
                    st.markdown('<div class="individual-card">', unsafe_allow_html=True)
                    
                    col1, col2, col3, col4, col5 = st.columns([1, 2, 3, 1, 1])
                    
                    with col1:
                        # Deputy photo
                        photo_path = get_deputy_photo(person_data['deputy_index'])
                        if photo_path:
                            st.markdown('<div class="photo-main">', unsafe_allow_html=True)
                            st.image(photo_path, use_column_width=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.info("📷 Sin foto")
                    
                    with col3:
                        # Personal information
                        st.markdown(f"""
                        <h2 style="color: white; margin-top: 0;">{person_data['Nombre']}</h2>
                        <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem;">
                            📍 <strong>{person_data['Circunscripción']}</strong> | 🏛️ {person_data['Cargo']}
                        </p>
                        <p style="color: rgba(255,255,255,0.8);">
                            👤 {person_data['Estado Civil']} | 📋 {person_data['Régimen Económico']}
                        </p>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        # Party logo
                        party_logo = get_party_logo(person_data['Circunscripción'], person_data['Nombre'])
                        if party_logo and os.path.exists(party_logo):
                            st.image(party_logo, caption="Partido", use_column_width=True)
                    
                    with col5:
                        # Hemiciclo seat
                        seat_path = get_hemiciclo_seat(person_data['deputy_index'])
                        if seat_path:
                            st.image(seat_path, caption="Escaño", use_column_width=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Financial metrics with spectacular design
                    st.markdown("---")
                    st.markdown("### 💰 Información Financiera")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="metric-container">
                            <div class="metric-label">Ingresos Declarados</div>
                            <div class="metric-value">€{person_data['Ingresos Declarados']:,.0f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="metric-container">
                            <div class="metric-label">Activos Líquidos</div>
                            <div class="metric-value">€{person_data['Activos Líquidos']:,.0f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div class="metric-container">
                            <div class="metric-label">Deudas</div>
                            <div class="metric-value">€{person_data['Deudas']:,.0f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown(f"""
                        <div class="metric-container">
                            <div class="metric-label">Posición Neta</div>
                            <div class="metric-value">€{person_data['Posición Neta']:,.0f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Additional metrics
                    st.markdown("### 🏠 Patrimonio")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("IRPF Pagado", f"€{person_data['IRPF Pagado']:,.0f}")
                    with col2:
                        st.metric("Propiedades Urbanas", f"{int(person_data['Propiedades Urbanas'])}")
                    with col3:
                        st.metric("Propiedades Rústicas", f"{int(person_data['Propiedades Rústicas'])}")
                    with col4:
                        st.metric("Vehículos", f"{int(person_data['Vehículos'])}")
        
        else:
            # Comparison mode
            st.markdown("### 📊 Comparación entre Parlamentarios")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="comparison-card">', unsafe_allow_html=True)
                names1 = sorted(df['Nombre'].unique())
                selected_name1 = st.selectbox("Primer parlamentario:", names1, key="compare1")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="comparison-card">', unsafe_allow_html=True)
                names2 = sorted(df['Nombre'].unique())
                selected_name2 = st.selectbox("Segundo parlamentario:", names2, key="compare2")
                st.markdown('</div>', unsafe_allow_html=True)
            
            if selected_name1 and selected_name2:
                person1 = df[df['Nombre'] == selected_name1].iloc[0]
                person2 = df[df['Nombre'] == selected_name2].iloc[0]
                
                st.markdown('<h2 class="vs-header">VS</h2>', unsafe_allow_html=True)
                
                # Comparison metrics
                metrics = [
                    ('Ingresos Declarados', '€'),
                    ('Activos Líquidos', '€'),
                    ('Deudas', '€'),
                    ('Posición Neta', '€'),
                    ('IRPF Pagado', '€'),
                    ('Total Propiedades', ''),
                    ('Vehículos', '')
                ]
                
                for metric, prefix in metrics:
                    col1, col2, col3 = st.columns([2, 1, 2])
                    
                    with col1:
                        value1 = person1[metric]
                        if prefix == '€':
                            st.metric(selected_name1[:20], f"{prefix}{value1:,.0f}")
                        else:
                            st.metric(selected_name1[:20], f"{int(value1)}")
                    
                    with col2:
                        st.markdown(f"<p style='text-align: center; color: rgba(255,255,255,0.5); margin-top: 20px;'>{metric}</p>", unsafe_allow_html=True)
                    
                    with col3:
                        value2 = person2[metric]
                        if prefix == '€':
                            st.metric(selected_name2[:20], f"{prefix}{value2:,.0f}")
                        else:
                            st.metric(selected_name2[:20], f"{int(value2)}")
    
    with tab2:
        st.markdown("### 📊 Tabla de Datos Completa con Filtros")
        
        # Advanced filters in expandable section
        with st.expander("🔧 Filtros Avanzados", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                min_income = st.number_input("Ingresos mínimos (€):", min_value=0, value=0, step=10000)
                max_income = st.number_input("Ingresos máximos (€):", min_value=0, value=10000000, step=10000)
            
            with col2:
                min_assets = st.number_input("Activos mínimos (€):", min_value=0, value=0, step=10000)
                max_debt = st.number_input("Deuda máxima (€):", min_value=0, value=10000000, step=10000)
            
            with col3:
                unique_constituencies = df['Circunscripción'].dropna().unique().tolist()
                constituencies = ['Todas'] + sorted([c for c in unique_constituencies if c])
                selected_constituency = st.selectbox("Circunscripción:", constituencies)
                
                min_properties = st.number_input("Mínimo propiedades:", min_value=0, value=0, step=1)
            
            with col4:
                sort_by = st.selectbox("Ordenar por:", 
                    ['Ingresos Declarados', 'Activos Líquidos', 'Posición Neta', 'Deudas', 'IRPF Pagado'])
                sort_order = st.radio("Orden:", ['Descendente', 'Ascendente'])
        
        # Apply filters
        filtered_df = df.copy()
        
        if min_income > 0:
            filtered_df = filtered_df[filtered_df['Ingresos Declarados'] >= min_income]
        if max_income < 10000000:
            filtered_df = filtered_df[filtered_df['Ingresos Declarados'] <= max_income]
        if min_assets > 0:
            filtered_df = filtered_df[filtered_df['Activos Líquidos'] >= min_assets]
        if max_debt < 10000000:
            filtered_df = filtered_df[filtered_df['Deudas'] <= max_debt]
        if selected_constituency != 'Todas':
            filtered_df = filtered_df[filtered_df['Circunscripción'] == selected_constituency]
        if min_properties > 0:
            filtered_df = filtered_df[filtered_df['Total Propiedades'] >= min_properties]
        
        # Sort
        filtered_df = filtered_df.sort_values(sort_by, ascending=(sort_order == 'Ascendente'))
        
        # Show results
        st.markdown(f"""
        <div class="info-card">
            📊 Mostrando <strong>{len(filtered_df)}</strong> de <strong>{len(df)}</strong> parlamentarios
        </div>
        """, unsafe_allow_html=True)
        
        # Format for display
        display_df = filtered_df.copy()
        money_cols = ['Ingresos Declarados', 'Activos Líquidos', 'Deudas', 'Posición Neta', 'IRPF Pagado']
        for col in money_cols:
            display_df[col] = display_df[col].apply(lambda x: f'€{x:,.0f}')
        
        # Remove deputy_index
        display_df = display_df.drop(columns=['deputy_index'])
        
        # Display with style
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=600
        )
        
        # Export options
        col1, col2 = st.columns(2)
        with col1:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="⬇️ Descargar datos filtrados (CSV)",
                data=csv,
                file_name='declaraciones_filtradas.csv',
                mime='text/csv'
            )
        
        with col2:
            # Summary statistics
            if len(filtered_df) > 0:
                avg_income = filtered_df['Ingresos Declarados'].mean()
                total_assets = filtered_df['Activos Líquidos'].sum()
                st.markdown(f"""
                <div class="info-card">
                    📈 <strong>Resumen:</strong> Ingreso medio: €{avg_income:,.0f} | Total activos: €{total_assets:,.0f}
                </div>
                """, unsafe_allow_html=True)

else:
    st.error("Error al cargar los datos. Verifique que existe el archivo 'all_deputies_merged.json'")

# Footer with style
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: rgba(255, 255, 255, 0.5); padding: 30px 0;'>
    <p>🏛️ Datos públicos del Congreso de los Diputados</p>
    <p>Desarrollado por <a href='https://twitter.com/Gsnchez' style='color: #667eea; text-decoration: none;'>@Gsnchez</a></p>
</div>
""", unsafe_allow_html=True)
