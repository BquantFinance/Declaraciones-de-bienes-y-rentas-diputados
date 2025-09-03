import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import re
from pathlib import Path

# Page configuration - MUST BE FIRST
st.set_page_config(
    page_title="Congreso Analytics XV | @Gsnchez",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark mode CSS with glassmorphism and gradients
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
        padding: 60px 40px;
        border-radius: 30px;
        margin-bottom: 40px;
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
        font-size: 3.5rem;
        font-weight: 900;
        margin-bottom: 10px;
        letter-spacing: -2px;
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.2rem;
        font-weight: 300;
        margin-bottom: 30px;
        position: relative;
        z-index: 1;
    }
    
    /* Property card */
    .property-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        transition: all 0.3s ease;
    }
    
    .property-card:hover {
        background: rgba(255, 255, 255, 0.05);
        transform: translateX(5px);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    .property-type {
        color: #667eea;
        font-weight: 600;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    
    .property-location {
        color: white;
        font-weight: 500;
        font-size: 1rem;
        margin-bottom: 5px;
    }
    
    .property-details {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    .property-year {
        color: #2ecc71;
        font-weight: 500;
    }
    
    .vehicle-card {
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.1), rgba(255, 152, 0, 0.1));
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 193, 7, 0.2);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        transition: all 0.3s ease;
    }
    
    .vehicle-card:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 20px rgba(255, 193, 7, 0.2);
    }
    
    .vehicle-model {
        color: #ffc107;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .vehicle-year {
        color: rgba(255, 255, 255, 0.8);
        font-weight: 400;
    }
    
    /* Metric cards */
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
    
    /* Individual card */
    .individual-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        backdrop-filter: blur(10px);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 25px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.2);
    }
    
    .individual-name {
        font-size: 2rem;
        font-weight: 800;
        color: white;
        margin-bottom: 10px;
    }
    
    .individual-info {
        color: rgba(255, 255, 255, 0.8);
        font-size: 1rem;
        margin: 5px 0;
    }
    
    .income-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.2), rgba(255, 152, 0, 0.2));
        padding: 10px 20px;
        border-radius: 15px;
        color: #ffc107;
        font-weight: 700;
        margin: 10px 0;
        font-size: 1.1rem;
    }
    
    /* Data tables */
    .dataframe {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }
    
    .dataframe thead tr th {
        background: rgba(102, 126, 234, 0.2) !important;
        color: white !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        font-size: 0.8rem !important;
        letter-spacing: 1px !important;
        padding: 15px !important;
        border: none !important;
    }
    
    .dataframe tbody tr {
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
        transition: all 0.2s ease !important;
    }
    
    .dataframe tbody tr:hover {
        background: rgba(102, 126, 234, 0.1) !important;
    }
    
    .dataframe tbody tr td {
        color: rgba(255, 255, 255, 0.9) !important;
        padding: 12px !important;
        font-size: 0.9rem !important;
    }
    
    /* Section headers */
    h1, h2, h3 {
        color: white !important;
        font-weight: 800 !important;
    }
    
    /* Tabs */
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
    }
    
    /* Buttons */
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
    
    /* Info boxes */
    .stInfo {
        background: rgba(52, 152, 219, 0.1) !important;
        border: 1px solid rgba(52, 152, 219, 0.3) !important;
        border-radius: 10px !important;
        color: #3498db !important;
    }
    
    .stSuccess {
        background: rgba(46, 204, 113, 0.1) !important;
        border: 1px solid rgba(46, 204, 113, 0.3) !important;
        border-radius: 10px !important;
        color: #2ecc71 !important;
    }
    
    .stWarning {
        background: rgba(255, 193, 7, 0.1) !important;
        border: 1px solid rgba(255, 193, 7, 0.3) !important;
        border-radius: 10px !important;
        color: #ffc107 !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Download button */
    .stDownloadButton button {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%) !important;
    }
    
    /* Metrics in Streamlit */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="metric-container"] label {
        color: rgba(255, 255, 255, 0.7) !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: white !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions to parse property details
def parse_property_details(details_str):
    """Parse property details string into structured format"""
    if pd.isna(details_str) or not details_str:
        return []
    
    # Split by 'clase:' to separate different properties
    properties = []
    parts = details_str.split('| clase:')
    if not parts[0].startswith('clase:'):
        parts[0] = 'clase:' + parts[0]
    
    for part in parts:
        if not part.strip():
            continue
            
        property_info = {}
        
        # Extract type (Piso, Finca, Plaza garaje, etc.)
        type_match = re.search(r'clase:([^;]+)', part)
        if type_match:
            property_info['tipo'] = type_match.group(1).strip()
        
        # Extract location
        location_match = re.search(r'situacion:([^;]+)', part)
        if location_match:
            property_info['ubicacion'] = location_match.group(1).strip()
        
        # Extract acquisition date
        date_match = re.search(r'fecha_adquisicion:(\d{4})', part)
        if date_match:
            property_info['año'] = date_match.group(1)
        
        # Extract ownership right
        right_match = re.search(r'derecho:([^;]+)', part)
        if right_match:
            property_info['derecho'] = right_match.group(1).strip()
        
        # Extract title
        title_match = re.search(r'titulo:([^;|]+)', part)
        if title_match:
            property_info['titulo'] = title_match.group(1).strip()
        
        if property_info:
            properties.append(property_info)
    
    return properties

def parse_vehicle_details(details_str):
    """Parse vehicle details string into structured format"""
    if pd.isna(details_str) or not details_str:
        return []
    
    vehicles = []
    # Split by common separators
    parts = re.split(r'\|', details_str)
    
    for part in parts:
        if not part.strip():
            continue
            
        vehicle_info = {}
        
        # Extract year
        year_match = re.search(r'fecha_adquisicion:(\d{4})', part)
        if year_match:
            vehicle_info['año'] = year_match.group(1)
        
        # Extract description/model
        desc_match = re.search(r'descripcion:([^;|]+)', part)
        if desc_match:
            vehicle_info['modelo'] = desc_match.group(1).strip()
        
        if vehicle_info:
            vehicles.append(vehicle_info)
    
    return vehicles

# Load data function
@st.cache_data
def load_data():
    df = pd.read_csv('datos_congreso_estructura_oficial.csv')
    
    # Convert numeric columns safely
    numeric_cols = [
        'total_income_declared', 'total_liquid_assets', 'posicion_neta_liquida',
        'deposits_total_balance', 'debts_pending_balance', 'irpf_paid_amount',
        'income_salary_total', 'income_dividends_total', 'income_interest_total',
        'income_other_total', 'property_value_other_undeclared'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Clean string columns
    string_cols = ['name_surname', 'position', 'constituency', 'legislatura', 'marital_status']
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].fillna('').str.strip()
    
    return df

# Hero Section
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">CONGRESO ANALYTICS</h1>
    <p class="hero-subtitle">XV Legislatura - Transparencia Parlamentaria</p>
    <a href="https://twitter.com/Gsnchez" target="_blank" style="display: inline-block; background: rgba(255, 255, 255, 0.2); backdrop-filter: blur(10px); padding: 12px 24px; border-radius: 50px; color: white; font-weight: 600; text-decoration: none; transition: all 0.3s ease; position: relative; z-index: 1;">
        Desarrollado por @Gsnchez ✨
    </a>
</div>
""", unsafe_allow_html=True)

# Disclaimer
st.markdown("""
<div class="disclaimer-glass">
    <h3 style="color: #ffc107; margin-top: 0;">⚠️ Descargo de responsabilidad</h3>
    <p><strong>Esta aplicación recopila información pública del Congreso de los Diputados.</strong> 
    No tiene afiliación oficial. Los datos pueden contener errores u omisiones.</p>
</div>
""", unsafe_allow_html=True)

# Load data
try:
    df = load_data()
    # Filter only XV Legislatura by default
    df = df[df['legislatura'] == 'XV'].copy()
    data_loaded = True
except Exception as e:
    st.error(f"Error al cargar datos: {str(e)}")
    data_loaded = False
    df = pd.DataFrame()

if data_loaded and not df.empty:
    # Main navigation
    st.markdown("---")
    mode = st.radio(
        "**Modo de análisis:**",
        ["🎯 Vista Rápida", "👤 Análisis Individual", "📊 Estadísticas"],
        horizontal=True
    )
    
    if mode == "🎯 Vista Rápida":
        # Quick stats for XV Legislature
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_parliamentarians = len(df['name_surname'].unique())
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Parlamentarios XV</div>
                <div class="metric-value">{total_parliamentarians}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_income = df['total_income_declared'].mean()
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Ingreso Promedio</div>
                <div class="metric-value">€{avg_income:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            median_assets = df['total_liquid_assets'].median()
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Mediana Activos</div>
                <div class="metric-value">€{median_assets:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            max_income = df['total_income_declared'].max()
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Ingreso Máximo</div>
                <div class="metric-value">€{max_income:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Top earners table
        st.markdown("### 💎 Top 15 Mayores Ingresos - XV Legislatura")
        top_earners = df.nlargest(15, 'total_income_declared')[
            ['name_surname', 'position', 'constituency', 'total_income_declared', 'total_liquid_assets']
        ].copy()
        top_earners['total_income_declared'] = top_earners['total_income_declared'].apply(lambda x: f'€{x:,.0f}')
        top_earners['total_liquid_assets'] = top_earners['total_liquid_assets'].apply(lambda x: f'€{x:,.0f}')
        top_earners.columns = ['Nombre', 'Cargo', 'Circunscripción', 'Ingresos', 'Activos']
        st.dataframe(top_earners, use_container_width=True, hide_index=True)
        
        # Distribution summary
        st.markdown("### 📊 Distribución de Ingresos")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            low = len(df[df['total_income_declared'] < 50000])
            st.info(f"**Rango inferior a €50.000**: {low} parlamentarios ({low/len(df)*100:.1f}%)")
        
        with col2:
            mid = len(df[(df['total_income_declared'] >= 50000) & (df['total_income_declared'] < 100000)])
            st.warning(f"**Rango €50.000 - €100.000**: {mid} parlamentarios ({mid/len(df)*100:.1f}%)")
        
        with col3:
            high = len(df[df['total_income_declared'] >= 100000])
            st.success(f"**Rango superior a €100.000**: {high} parlamentarios ({high/len(df)*100:.1f}%)")
    
    elif mode == "👤 Análisis Individual":
        st.markdown("### 🔍 Búsqueda Individual - XV Legislatura")
        
        # Search box
        search_term = st.text_input("🔎 Buscar por nombre:", placeholder="Escribe parte del nombre...")
        
        if search_term:
            filtered_names = df[df['name_surname'].str.contains(search_term, case=False, na=False)]['name_surname'].unique()
            if len(filtered_names) > 0:
                selected_name = st.selectbox("Selecciona parlamentario:", filtered_names)
            else:
                st.warning("No se encontraron resultados")
                selected_name = None
        else:
            names = sorted(df['name_surname'].unique())
            selected_name = st.selectbox("👤 Selecciona parlamentario:", names)
        
        if selected_name:
            person_data = df[df['name_surname'] == selected_name].iloc[0]
            
            # Individual card
            st.markdown(f"""
            <div class="individual-card">
                <h2 class="individual-name">{person_data['name_surname']}</h2>
                <p class="individual-info">📍 {person_data['constituency']} | 🏛️ {person_data['position']}</p>
                <div class="income-badge">💰 Ingresos: €{person_data['total_income_declared']:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Tabs for details
            tab1, tab2, tab3 = st.tabs(["💵 Ingresos y Activos", "🏠 Propiedades", "📄 Todos los Datos"])
            
            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### 💰 Ingresos")
                    st.metric("Total Declarado", f"€{person_data['total_income_declared']:,.0f}")
                    if 'income_salary_total' in person_data:
                        st.metric("Salarios", f"€{person_data['income_salary_total']:,.0f}")
                    if 'irpf_paid_amount' in person_data:
                        st.metric("IRPF Pagado", f"€{person_data['irpf_paid_amount']:,.0f}")
                
                with col2:
                    st.markdown("#### 💎 Activos")
                    st.metric("Activos Líquidos", f"€{person_data['total_liquid_assets']:,.0f}")
                    st.metric("Posición Neta", f"€{person_data['posicion_neta_liquida']:,.0f}")
                    if 'deposits_total_balance' in person_data:
                        st.metric("Depósitos", f"€{person_data['deposits_total_balance']:,.0f}")
            
            with tab2:
                st.markdown("#### 🏘️ Propiedades e Inmuebles")
                
                # Urban properties
                if 'property_num_urban' in df.columns and person_data.get('property_num_urban', 0) > 0:
                    st.markdown(f"**🏢 Inmuebles Urbanos ({int(person_data['property_num_urban'])})**")
                    
                    if 'property_details_urban' in df.columns and pd.notna(person_data['property_details_urban']):
                        urban_props = parse_property_details(person_data['property_details_urban'])
                        if urban_props:
                            for prop in urban_props:
                                st.markdown(f"""
                                <div class="property-card">
                                    <div class="property-type">{prop.get('tipo', 'Inmueble')}</div>
                                    <div class="property-location">📍 {prop.get('ubicacion', 'No especificado')}</div>
                                    <div class="property-details">
                                        <span class="property-year">Año: {prop.get('año', 'No especificado')}</span> | 
                                        Derecho: {prop.get('derecho', 'No especificado')} | 
                                        Título: {prop.get('titulo', 'No especificado')}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info(person_data['property_details_urban'])
                
                # Rural properties
                if 'property_num_rural' in df.columns and person_data.get('property_num_rural', 0) > 0:
                    st.markdown(f"**🌾 Inmuebles Rústicos ({int(person_data['property_num_rural'])})**")
                    
                    if 'property_details_rural' in df.columns and pd.notna(person_data['property_details_rural']):
                        rural_props = parse_property_details(person_data['property_details_rural'])
                        if rural_props:
                            for prop in rural_props:
                                st.markdown(f"""
                                <div class="property-card">
                                    <div class="property-type">{prop.get('tipo', 'Finca')}</div>
                                    <div class="property-location">📍 {prop.get('ubicacion', 'No especificado')}</div>
                                    <div class="property-details">
                                        <span class="property-year">Año: {prop.get('año', 'No especificado')}</span> | 
                                        Derecho: {prop.get('derecho', 'No especificado')} | 
                                        Título: {prop.get('titulo', 'No especificado')}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info(person_data['property_details_rural'])
                
                # Vehicles
                if 'vehicles_num' in df.columns and person_data.get('vehicles_num', 0) > 0:
                    st.markdown(f"**🚗 Vehículos ({int(person_data['vehicles_num'])})**")
                    
                    if 'vehicles_description' in df.columns and pd.notna(person_data['vehicles_description']):
                        vehicles = parse_vehicle_details(person_data['vehicles_description'])
                        if vehicles:
                            for vehicle in vehicles:
                                st.markdown(f"""
                                <div class="vehicle-card">
                                    <div class="vehicle-model">🚗 {vehicle.get('modelo', 'Vehículo')}</div>
                                    <div class="vehicle-year">Año de adquisición: {vehicle.get('año', 'No especificado')}</div>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.warning(person_data['vehicles_description'])
                
                if (person_data.get('property_num_urban', 0) == 0 and 
                    person_data.get('property_num_rural', 0) == 0 and 
                    person_data.get('vehicles_num', 0) == 0):
                    st.info("No se declaran propiedades")
            
            with tab3:
                st.markdown("#### 📄 Todos los Datos Disponibles")
                
                # Show observations if available
                if 'observaciones' in df.columns and pd.notna(person_data['observaciones']):
                    st.warning(f"**📝 Observaciones:** {person_data['observaciones']}")
                
                # Display all non-empty fields in a structured way
                col1, col2 = st.columns(2)
                
                # Financial data
                with col1:
                    st.markdown("**💰 Datos Financieros**")
                    financial_fields = [
                        ('Total Ingresos', 'total_income_declared'),
                        ('Salarios', 'income_salary_total'),
                        ('Dividendos', 'income_dividends_total'),
                        ('Intereses', 'income_interest_total'),
                        ('IRPF Pagado', 'irpf_paid_amount'),
                        ('Activos Líquidos', 'total_liquid_assets'),
                        ('Depósitos', 'deposits_total_balance'),
                        ('Posición Neta', 'posicion_neta_liquida'),
                        ('Deudas', 'debts_pending_balance')
                    ]
                    
                    for label, field in financial_fields:
                        if field in person_data and pd.notna(person_data[field]) and person_data[field] != 0:
                            st.write(f"• {label}: €{person_data[field]:,.0f}")
                
                # Personal and property data
                with col2:
                    st.markdown("**📋 Datos Personales**")
                    if 'marital_status' in person_data and pd.notna(person_data['marital_status']):
                        st.write(f"• Estado Civil: {person_data['marital_status']}")
                    if 'economic_regime' in person_data and pd.notna(person_data['economic_regime']):
                        st.write(f"• Régimen Económico: {person_data['economic_regime']}")
                    
                    st.markdown("**🏠 Propiedades**")
                    property_fields = [
                        ('Inmuebles Urbanos', 'property_num_urban'),
                        ('Inmuebles Rústicos', 'property_num_rural'),
                        ('Vehículos', 'vehicles_num'),
                        ('Sociedades No Cotizadas', 'companies_unlisted_num'),
                        ('Cuentas Bancarias', 'deposits_num_accounts')
                    ]
                    
                    for label, field in property_fields:
                        if field in person_data and pd.notna(person_data[field]) and person_data[field] != 0:
                            st.write(f"• {label}: {int(person_data[field])}")
    
    elif mode == "📊 Estadísticas":
        st.markdown("### 📊 Estadísticas XV Legislatura")
        
        # Summary by position
        st.markdown("#### Por Cargo")
        position_summary = df.groupby('position').agg({
            'total_income_declared': ['mean', 'median', 'count'],
            'total_liquid_assets': 'mean'
        }).round(0)
        
        position_summary.columns = ['Ingreso Medio', 'Ingreso Mediano', 'Cantidad', 'Activos Medios']
        position_summary = position_summary.sort_values('Ingreso Medio', ascending=False)
        
        # Format for display
        for col in ['Ingreso Medio', 'Ingreso Mediano', 'Activos Medios']:
            position_summary[col] = position_summary[col].apply(lambda x: f'€{x:,.0f}')
        
        st.dataframe(position_summary, use_container_width=True)
        
        # Top constituencies
        st.markdown("#### Top 10 Circunscripciones por Ingreso Medio")
        const_summary = df.groupby('constituency').agg({
            'total_income_declared': ['mean', 'count']
        }).round(0)
        
        const_summary.columns = ['Ingreso Medio', 'Parlamentarios']
        const_summary = const_summary.sort_values('Ingreso Medio', ascending=False).head(10)
        const_summary['Ingreso Medio'] = const_summary['Ingreso Medio'].apply(lambda x: f'€{x:,.0f}')
        
        st.dataframe(const_summary, use_container_width=True)
        
        # Property statistics
        st.markdown("#### Estadísticas de Propiedades")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_urban = df['property_num_urban'].mean() if 'property_num_urban' in df.columns else 0
            st.metric("Media Inmuebles Urbanos", f"{avg_urban:.1f}")
        
        with col2:
            avg_rural = df['property_num_rural'].mean() if 'property_num_rural' in df.columns else 0
            st.metric("Media Inmuebles Rústicos", f"{avg_rural:.1f}")
        
        with col3:
            avg_vehicles = df['vehicles_num'].mean() if 'vehicles_num' in df.columns else 0
            st.metric("Media Vehículos", f"{avg_vehicles:.1f}")
        
        # Export
        st.markdown("---")
        csv = df.to_csv(index=False)
        st.download_button(
            label="⬇️ Descargar datos XV Legislatura (CSV)",
            data=csv,
            file_name='congreso_xv_legislatura.csv',
            mime='text/csv'
        )

else:
    st.error("⚠️ No se pudieron cargar los datos. Verifica el archivo CSV.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: rgba(255, 255, 255, 0.5); padding: 30px 0;'>
    <p>⚡ Datos públicos del Congreso - XV Legislatura</p>
    <p>Desarrollado por <a href='https://twitter.com/Gsnchez' style='color: #667eea; text-decoration: none;'>@Gsnchez</a></p>
</div>
""", unsafe_allow_html=True)
