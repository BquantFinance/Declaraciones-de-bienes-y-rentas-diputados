import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import re
from pathlib import Path
import requests
from PIL import Image
from io import BytesIO

# Page configuration - MUST BE FIRST
st.set_page_config(
    page_title="Declaraciones de Bienes y Rentas | XV Legislatura",
    page_icon="🏛️",
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

# Configuration for image paths
IMAGE_FOLDER = "fotos_diputados"  # Folder with deputy photos from GitHub

def get_deputy_image(source_file):
    """Get the deputy image path from source_file column"""
    if pd.isna(source_file):
        return None
    
    try:
        # Extract the deputy number from source_file
        # Example: deputy_001_assets_000005_000_e_0000017_20190502_1.pdf -> 001
        parts = source_file.split('_')
        if len(parts) >= 2 and parts[0] == 'deputy':
            deputy_num = parts[1]  # e.g., "001"
            
            # The images in GitHub are named like: 001.jpg, 002.jpg, etc.
            image_path = os.path.join(IMAGE_FOLDER, f"{deputy_num}.jpg")
            if os.path.exists(image_path):
                return image_path
            
            # Also try with leading zeros variations
            image_path = os.path.join(IMAGE_FOLDER, f"{int(deputy_num)}.jpg")
            if os.path.exists(image_path):
                return image_path
    except:
        pass
    
    return None

def get_deputy_image_url(source_file):
    """Get GitHub URL for deputy image if local file doesn't exist"""
    if pd.isna(source_file):
        return None
    
    try:
        parts = source_file.split('_')
        if len(parts) >= 2 and parts[0] == 'deputy':
            deputy_num = parts[1]
            # Direct GitHub raw URL
            github_url = f"https://raw.githubusercontent.com/BquantFinance/Declaraciones-de-bienes-y-rentas-diputados/main/fotos_diputados/{deputy_num}.jpg"
            return github_url
    except:
        pass
    
    return None

@st.cache_data
def load_image_from_url(url):
    """Load image from URL with caching"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            return img
        return None
    except:
        return None

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
    <h1 class="hero-title">DECLARACIONES DE BIENES Y RENTAS</h1>
    <p class="hero-subtitle">XV Legislatura - Congreso de los Diputados</p>
    <a href="https://twitter.com/Gsnchez" target="_blank" style="display: inline-block; background: rgba(255, 255, 255, 0.2); backdrop-filter: blur(10px); padding: 12px 24px; border-radius: 50px; color: white; font-weight: 600; text-decoration: none; transition: all 0.3s ease; position: relative; z-index: 1;">
        Desarrollado por @Gsnchez ✨
    </a>
</div>
""", unsafe_allow_html=True)

# Setup instructions
st.markdown("""
<div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15)); backdrop-filter: blur(10px); border: 2px solid rgba(102, 126, 234, 0.4); border-radius: 20px; padding: 25px; margin: 20px 0; color: white;">
    <h4 style="color: #667eea; margin-top: 0; text-align: center;">⚙️ Configuración Óptima de Visualización</h4>
    <p style="line-height: 1.8; text-align: center; font-size: 1.05rem;">
        <strong>Esta aplicación ha sido diseñada para visualizarse en:</strong>
    </p>
    <div style="display: flex; justify-content: space-around; margin: 20px 0;">
        <div style="text-align: center; flex: 1;">
            <div style="font-size: 2rem; margin-bottom: 10px;">🖥️</div>
            <strong style="color: #667eea;">Resolución de PC</strong><br>
            <span style="font-size: 0.9rem; color: rgba(255,255,255,0.8);">Mínimo 1920x1080 (Full HD)<br>Recomendado: 2560x1440 o superior</span>
        </div>
        <div style="text-align: center; flex: 1;">
            <div style="font-size: 2rem; margin-bottom: 10px;">🌙</div>
            <strong style="color: #667eea;">Modo Oscuro del Navegador</strong><br>
            <span style="font-size: 0.9rem; color: rgba(255,255,255,0.8);">Chrome/Edge: Configuración → Apariencia → Tema Oscuro<br>Firefox: Configuración → General → Tema Oscuro</span>
        </div>
    </div>
    <p style="text-align: center; font-size: 0.9rem; color: rgba(255,255,255,0.7); margin-top: 15px;">
        La experiencia visual óptima requiere estas configuraciones para apreciar correctamente el diseño glassmórfico y los gradientes.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: linear-gradient(135deg, rgba(46, 204, 113, 0.1), rgba(52, 152, 219, 0.1)); backdrop-filter: blur(10px); border: 1px solid rgba(46, 204, 113, 0.3); border-radius: 15px; padding: 15px; margin: 20px 0; color: #2ecc71; text-align: center;">
    <strong>📸 Sistema de Visualización Fotográfica</strong><br>
    <span style="font-size: 0.9rem;">Las fotografías de los parlamentarios se cargan automáticamente desde el repositorio oficial. 
    Para optimizar el rendimiento, puede descargar el conjunto completo desde el 
    <a href="https://github.com/BquantFinance/Declaraciones-de-bienes-y-rentas-diputados/tree/main/fotos_diputados" target="_blank" style="color: #3498db;">
    repositorio de GitHub</a> y almacenarlo localmente en el directorio 'fotos_diputados'.</span>
</div>
""", unsafe_allow_html=True)

# Project motivation
st.markdown("""
<div style="background: rgba(102, 126, 234, 0.1); backdrop-filter: blur(10px); border: 1px solid rgba(102, 126, 234, 0.2); border-radius: 20px; padding: 30px; margin: 20px 0; color: white;">
    <h3 style="color: #667eea; margin-top: 0; text-align: center;">📚 Motivación del Proyecto</h3>
    <p style="line-height: 1.8; text-align: justify;">
        Este proyecto surge con el propósito fundamental de <strong>democratizar el acceso a la información pública</strong> 
        relativa a las declaraciones de bienes y rentas de los parlamentarios españoles. La iniciativa busca transformar 
        documentos dispersos y de difícil consulta en una plataforma <strong>accesible, estructurada y comprensible</strong> 
        para todos los ciudadanos.
    </p>
    <p style="line-height: 1.8; text-align: justify;">
        Los objetivos principales de esta herramienta son:
    </p>
    <ul style="line-height: 1.8;">
        <li><strong>Transparencia:</strong> Facilitar el escrutinio público de la información patrimonial de los representantes electos, 
        fortaleciendo así los mecanismos de rendición de cuentas democráticos.</li>
        <li><strong>Accesibilidad:</strong> Eliminar las barreras técnicas que dificultan el acceso a estos datos, 
        proporcionando una interfaz intuitiva y amigable para cualquier ciudadano.</li>
        <li><strong>Estructuración:</strong> Organizar sistemáticamente la información dispersa en múltiples documentos PDF, 
        convirtiéndola en datos estructurados que permiten análisis comparativos y agregados.</li>
    </ul>
    <p style="line-height: 1.8; text-align: justify;">
        La transparencia en la gestión pública constituye un pilar fundamental del sistema democrático, 
        y este proyecto aspira a contribuir a su fortalecimiento mediante el uso de tecnología al servicio de la ciudadanía.
    </p>
</div>
""", unsafe_allow_html=True)

# Disclaimer
st.markdown("""
<div class="disclaimer-glass">
    <h3 style="color: #ffc107; margin-top: 0;">⚠️ Descargo de Responsabilidad Legal</h3>
    <p style="line-height: 1.6; text-align: justify;">
        <strong>Esta aplicación constituye una herramienta independiente de análisis y visualización de información pública</strong> 
        disponible en el portal oficial del Congreso de los Diputados. No mantiene vinculación institucional alguna con el 
        Congreso de los Diputados, sus órganos de gobierno, ni cuenta con aval, autorización o respaldo oficial de dicha institución.
    </p>
    <p style="line-height: 1.6; text-align: justify;">
        Los datos presentados provienen de fuentes públicas oficiales y, si bien se ha procurado garantizar su exactitud mediante 
        procesos automatizados de extracción y estructuración, <strong>la aplicación podría contener errores, inexactitudes, 
        omisiones o información desactualizada</strong> derivados del procesamiento de los documentos originales. 
        Para consultas oficiales y verificación de la información, se recomienda acudir directamente a los documentos 
        originales publicados en el portal web del Congreso de los Diputados.
    </p>
    <p style="line-height: 1.6; text-align: justify;">
        El uso de esta herramienta es responsabilidad exclusiva del usuario, quien deberá ejercer su propio criterio 
        en la interpretación y utilización de los datos aquí presentados.
    </p>
</div>
""", unsafe_allow_html=True)

# Load data
try:
    df = load_data()
    # Filter only XV Legislature by default
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
        "**Seleccione el modo de visualización:**",
        ["📊 Resumen Ejecutivo", "🔍 Análisis Individual", "📈 Estadísticas Agregadas"],
        horizontal=True
    )
    
    if mode == "📊 Resumen Ejecutivo":
        # Quick stats for XV Legislature
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_parliamentarians = len(df['name_surname'].unique())
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Total Parlamentarios</div>
                <div class="metric-value">{total_parliamentarians}</div>
                <div class="metric-delta">XV Legislatura</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_income = df['total_income_declared'].mean()
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Ingreso Medio Anual</div>
                <div class="metric-value">€{avg_income:,.0f}</div>
                <div class="metric-delta">Valor promedio declarado</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            median_assets = df['total_liquid_assets'].median()
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Mediana de Activos</div>
                <div class="metric-value">€{median_assets:,.0f}</div>
                <div class="metric-delta">Activos líquidos</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            max_income = df['total_income_declared'].max()
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Máximo Declarado</div>
                <div class="metric-value">€{max_income:,.0f}</div>
                <div class="metric-delta">Mayor declaración</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Top earners table
        st.markdown("### 💎 Ranking de Mayores Declaraciones Patrimoniales - XV Legislatura")
        top_earners = df.nlargest(15, 'total_income_declared')[
            ['name_surname', 'position', 'constituency', 'total_income_declared', 'total_liquid_assets']
        ].copy()
        top_earners['total_income_declared'] = top_earners['total_income_declared'].apply(lambda x: f'€{x:,.0f}')
        top_earners['total_liquid_assets'] = top_earners['total_liquid_assets'].apply(lambda x: f'€{x:,.0f}')
        top_earners.columns = ['Nombre', 'Cargo', 'Circunscripción', 'Ingresos Declarados', 'Activos Líquidos']
        st.dataframe(top_earners, use_container_width=True, hide_index=True)
        
        # Distribution summary
        st.markdown("### 📊 Distribución de Ingresos Declarados")
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
    
    elif mode == "🔍 Análisis Individual":
        st.markdown("### 🔍 Consulta Individual de Parlamentarios - XV Legislatura")
        
        # Search box
        search_term = st.text_input("🔎 Búsqueda por nombre:", placeholder="Introduzca el nombre o apellidos del parlamentario...")
        
        if search_term:
            filtered_names = df[df['name_surname'].str.contains(search_term, case=False, na=False)]['name_surname'].unique()
            if len(filtered_names) > 0:
                selected_name = st.selectbox("Seleccione parlamentario:", filtered_names)
            else:
                st.warning("No se han encontrado coincidencias con los criterios de búsqueda especificados.")
                selected_name = None
        else:
            names = sorted(df['name_surname'].unique())
            selected_name = st.selectbox("Seleccione parlamentario:", names)
        
        if selected_name:
            person_data = df[df['name_surname'] == selected_name].iloc[0]
            
            # Check for deputy image (local or GitHub)
            deputy_image_path = get_deputy_image(person_data['source_file'])
            deputy_image_url = get_deputy_image_url(person_data['source_file'])
            
            # Create layout with image if available
            if deputy_image_path and os.path.exists(deputy_image_path):
                # Local image exists
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
                    st.image(deputy_image_path, caption=person_data['name_surname'], use_column_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="individual-card">
                        <h2 class="individual-name">{person_data['name_surname']}</h2>
                        <p class="individual-info">📍 {person_data['constituency']} | 🏛️ {person_data['position']}</p>
                        <div class="income-badge">💰 Ingresos Declarados: €{person_data['total_income_declared']:,.0f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            elif deputy_image_url:
                # Try to load from GitHub URL
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    img = load_image_from_url(deputy_image_url)
                    if img:
                        st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
                        st.image(img, caption=person_data['name_surname'], use_column_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.info("📷 Cargando imagen...")
                
                with col2:
                    st.markdown(f"""
                    <div class="individual-card">
                        <h2 class="individual-name">{person_data['name_surname']}</h2>
                        <p class="individual-info">📍 {person_data['constituency']} | 🏛️ {person_data['position']}</p>
                        <div class="income-badge">💰 Ingresos Declarados: €{person_data['total_income_declared']:,.0f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # No image available, show full width card
                st.markdown(f"""
                <div class="individual-card">
                    <h2 class="individual-name">{person_data['name_surname']}</h2>
                    <p class="individual-info">📍 {person_data['constituency']} | 🏛️ {person_data['position']}</p>
                    <div class="income-badge">💰 Ingresos Declarados: €{person_data['total_income_declared']:,.0f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Tabs for details
            tab1, tab2, tab3 = st.tabs(["💵 Información Económica", "🏠 Patrimonio Inmobiliario", "📄 Registro Completo"])
            
            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### 💰 Declaración de Ingresos")
                    st.metric("Ingresos Totales Declarados", f"€{person_data['total_income_declared']:,.0f}")
                    if 'income_salary_total' in person_data:
                        st.metric("Retribuciones Salariales", f"€{person_data['income_salary_total']:,.0f}")
                    if 'irpf_paid_amount' in person_data:
                        st.metric("IRPF Satisfecho", f"€{person_data['irpf_paid_amount']:,.0f}")
                
                with col2:
                    st.markdown("#### 💎 Activos Financieros")
                    st.metric("Activos Líquidos Totales", f"€{person_data['total_liquid_assets']:,.0f}")
                    st.metric("Posición Neta Patrimonial", f"€{person_data['posicion_neta_liquida']:,.0f}")
                    if 'deposits_total_balance' in person_data:
                        st.metric("Saldo en Depósitos Bancarios", f"€{person_data['deposits_total_balance']:,.0f}")
            
            with tab2:
                st.markdown("#### 🏘️ Declaración de Bienes Inmuebles y Vehículos")
                
                # Urban properties
                if 'property_num_urban' in df.columns and person_data.get('property_num_urban', 0) > 0:
                    st.markdown(f"**🏢 Bienes Inmuebles de Naturaleza Urbana ({int(person_data['property_num_urban'])})**")
                    
                    if 'property_details_urban' in df.columns and pd.notna(person_data['property_details_urban']):
                        urban_props = parse_property_details(person_data['property_details_urban'])
                        if urban_props:
                            for prop in urban_props:
                                st.markdown(f"""
                                <div class="property-card">
                                    <div class="property-type">{prop.get('tipo', 'Bien Inmueble')}</div>
                                    <div class="property-location">📍 Ubicación: {prop.get('ubicacion', 'No especificado')}</div>
                                    <div class="property-details">
                                        <span class="property-year">Año de adquisición: {prop.get('año', 'No especificado')}</span> | 
                                        Derecho: {prop.get('derecho', 'No especificado')} | 
                                        Título: {prop.get('titulo', 'No especificado')}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info(person_data['property_details_urban'])
                
                # Rural properties
                if 'property_num_rural' in df.columns and person_data.get('property_num_rural', 0) > 0:
                    st.markdown(f"**🌾 Bienes Inmuebles de Naturaleza Rústica ({int(person_data['property_num_rural'])})**")
                    
                    if 'property_details_rural' in df.columns and pd.notna(person_data['property_details_rural']):
                        rural_props = parse_property_details(person_data['property_details_rural'])
                        if rural_props:
                            for prop in rural_props:
                                st.markdown(f"""
                                <div class="property-card">
                                    <div class="property-type">{prop.get('tipo', 'Finca Rústica')}</div>
                                    <div class="property-location">📍 Ubicación: {prop.get('ubicacion', 'No especificado')}</div>
                                    <div class="property-details">
                                        <span class="property-year">Año de adquisición: {prop.get('año', 'No especificado')}</span> | 
                                        Derecho: {prop.get('derecho', 'No especificado')} | 
                                        Título: {prop.get('titulo', 'No especificado')}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info(person_data['property_details_rural'])
                
                # Vehicles
                if 'vehicles_num' in df.columns and person_data.get('vehicles_num', 0) > 0:
                    st.markdown(f"**🚗 Vehículos Declarados ({int(person_data['vehicles_num'])})**")
                    
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
                    st.info("No se han declarado bienes inmuebles ni vehículos en el registro patrimonial.")
            
            with tab3:
                st.markdown("#### 📄 Registro Completo de Declaraciones")
                
                # Show observations if available
                if 'observaciones' in df.columns and pd.notna(person_data['observaciones']):
                    st.warning(f"**📝 Observaciones del Declarante:** {person_data['observaciones']}")
                
                # Display all non-empty fields in a structured way
                col1, col2 = st.columns(2)
                
                # Financial data
                with col1:
                    st.markdown("**💰 Información Económica Detallada**")
                    financial_fields = [
                        ('Ingresos Totales Declarados', 'total_income_declared'),
                        ('Retribuciones Salariales', 'income_salary_total'),
                        ('Rendimientos por Dividendos', 'income_dividends_total'),
                        ('Rendimientos por Intereses', 'income_interest_total'),
                        ('IRPF Satisfecho', 'irpf_paid_amount'),
                        ('Activos Líquidos Totales', 'total_liquid_assets'),
                        ('Saldo en Depósitos', 'deposits_total_balance'),
                        ('Posición Patrimonial Neta', 'posicion_neta_liquida'),
                        ('Deudas Pendientes', 'debts_pending_balance')
                    ]
                    
                    for label, field in financial_fields:
                        if field in person_data and pd.notna(person_data[field]) and person_data[field] != 0:
                            st.write(f"• {label}: €{person_data[field]:,.0f}")
                
                # Personal and property data
                with col2:
                    st.markdown("**📋 Información Personal**")
                    if 'marital_status' in person_data and pd.notna(person_data['marital_status']):
                        st.write(f"• Estado Civil: {person_data['marital_status']}")
                    if 'economic_regime' in person_data and pd.notna(person_data['economic_regime']):
                        st.write(f"• Régimen Económico Matrimonial: {person_data['economic_regime']}")
                    
                    st.markdown("**🏠 Resumen Patrimonial**")
                    property_fields = [
                        ('Bienes Inmuebles Urbanos', 'property_num_urban'),
                        ('Bienes Inmuebles Rústicos', 'property_num_rural'),
                        ('Vehículos', 'vehicles_num'),
                        ('Sociedades No Cotizadas', 'companies_unlisted_num'),
                        ('Cuentas Bancarias', 'deposits_num_accounts')
                    ]
                    
                    for label, field in property_fields:
                        if field in person_data and pd.notna(person_data[field]) and person_data[field] != 0:
                            st.write(f"• {label}: {int(person_data[field])}")
    
    elif mode == "📈 Estadísticas Agregadas":
        st.markdown("### 📈 Análisis Estadístico Agregado - XV Legislatura")
        
        # Summary by position
        st.markdown("#### Análisis por Categoría Profesional")
        position_summary = df.groupby('position').agg({
            'total_income_declared': ['mean', 'median', 'count'],
            'total_liquid_assets': 'mean'
        }).round(0)
        
        position_summary.columns = ['Ingreso Medio', 'Ingreso Mediano', 'N° Parlamentarios', 'Activos Medios']
        position_summary = position_summary.sort_values('Ingreso Medio', ascending=False)
        
        # Format for display
        for col in ['Ingreso Medio', 'Ingreso Mediano', 'Activos Medios']:
            position_summary[col] = position_summary[col].apply(lambda x: f'€{x:,.0f}')
        
        st.dataframe(position_summary, use_container_width=True)
        
        # Top constituencies
        st.markdown("#### Ranking de Circunscripciones por Patrimonio Medio Declarado")
        const_summary = df.groupby('constituency').agg({
            'total_income_declared': ['mean', 'count']
        }).round(0)
        
        const_summary.columns = ['Ingreso Medio', 'N° Parlamentarios']
        const_summary = const_summary.sort_values('Ingreso Medio', ascending=False).head(10)
        const_summary['Ingreso Medio'] = const_summary['Ingreso Medio'].apply(lambda x: f'€{x:,.0f}')
        
        st.dataframe(const_summary, use_container_width=True)
        
        # Property statistics
        st.markdown("#### Análisis del Patrimonio Inmobiliario")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_urban = df['property_num_urban'].mean() if 'property_num_urban' in df.columns else 0
            st.metric("Promedio de Inmuebles Urbanos", f"{avg_urban:.2f}")
        
        with col2:
            avg_rural = df['property_num_rural'].mean() if 'property_num_rural' in df.columns else 0
            st.metric("Promedio de Inmuebles Rústicos", f"{avg_rural:.2f}")
        
        with col3:
            avg_vehicles = df['vehicles_num'].mean() if 'vehicles_num' in df.columns else 0
            st.metric("Promedio de Vehículos", f"{avg_vehicles:.2f}")
        
        # Export
        st.markdown("---")
        st.markdown("#### 📥 Exportación de Datos")
        csv = df.to_csv(index=False)
        st.download_button(
            label="⬇️ Descargar conjunto de datos completo XV Legislatura (formato CSV)",
            data=csv,
            file_name='declaraciones_bienes_rentas_xv_legislatura.csv',
            mime='text/csv'
        )

else:
    st.error("""
    ⚠️ **Error en la carga de datos**
    
    No se ha podido acceder al archivo de datos necesario para el funcionamiento de la aplicación. 
    Por favor, verifique que el archivo 'datos_congreso_estructura_oficial.csv' se encuentra en el directorio correspondiente.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: rgba(255, 255, 255, 0.5); padding: 30px 0;'>
    <p>🏛️ Declaraciones de Bienes y Rentas - Datos públicos del Congreso de los Diputados</p>
    <p>XV Legislatura | Transparencia y Accesibilidad</p>
    <p>Desarrollado por <a href='https://twitter.com/Gsnchez' style='color: #667eea; text-decoration: none;'>@Gsnchez</a></p>
</div>
""", unsafe_allow_html=True)
